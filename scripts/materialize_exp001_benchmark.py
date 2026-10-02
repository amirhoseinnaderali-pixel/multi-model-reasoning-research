#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from typing import Any

EXPECTED_SOURCE_TASK_COUNT = 164
REQUIRED_OUTPUT_FIELDS = {
    "task_id",
    "task_sha256",
    "test_sha256",
    "prompt",
    "entry_point",
    "visible_tests",
    "hidden_tests",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_task_hash(task: dict[str, Any]) -> str:
    payload = {
        "task_id": task["task_id"],
        "prompt": task["prompt"],
        "entry_point": task["entry_point"],
    }
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def test_source_hash(test_source: str) -> str:
    return sha256_text(test_source)


def strip_doctest_examples(prompt: str) -> str:
    lines = prompt.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*>>>\s", line):
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if re.match(r"^\s*>>>\s", nxt) or not nxt.strip():
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out).rstrip() + "\n"


def _check_function(test_source: str) -> ast.FunctionDef:
    tree = ast.parse(test_source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "check":
            return node
    raise ValueError("Test source does not define check(candidate)")


def _top_level_asserts(test_source: str) -> list[ast.Assert]:
    check = _check_function(test_source)
    asserts: list[ast.Assert] = []
    for node in check.body:
        if isinstance(node, ast.Assert):
            asserts.append(node)
        elif (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "print"
        ):
            continue
        elif (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue
        elif isinstance(node, (ast.Pass, ast.Return)):
            continue
        else:
            raise ValueError(
                f"Unsupported executable setup inside check(candidate): {ast.unparse(node)}"
            )
    return asserts


def split_assertions(test_source: str) -> tuple[list[str], list[str], int]:
    asserts = _top_level_asserts(test_source)
    if len(asserts) < 2:
        raise ValueError("Every EXP-001 task must contain at least two top-level assertions")
    cut = (len(asserts) + 1) // 2
    visible = [ast.unparse(node) for node in asserts[:cut]]
    hidden = [ast.unparse(node) for node in asserts[cut:]]
    return visible, hidden, len(asserts)


def _module_setup(test_source: str) -> str:
    tree = ast.parse(test_source)
    kept = [
        node
        for node in tree.body
        if not (isinstance(node, ast.FunctionDef) and node.name == "check")
    ]
    if not kept:
        return ""
    return "\n\n".join(ast.unparse(node) for node in kept) + "\n"


def _build_test_source(
    entry_point: str,
    test_source: str,
    assertions: list[str],
) -> str:
    setup = _module_setup(test_source)
    parts = []
    if setup.strip():
        parts.append(setup.rstrip())
    parts.append(f"from candidate import {entry_point} as candidate")
    parts.extend(assertions)
    return "\n\n".join(parts).rstrip() + "\n"


def fetch_source(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    provenance = manifest["provenance"]
    commit = provenance["source_commit"]
    url = f"https://raw.githubusercontent.com/openai/human-eval/{commit}/data/HumanEval.jsonl.gz"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "multi-model-reasoning-research/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        archive = response.read()

    expected_archive_hash = provenance["source_archive_sha256"]
    actual_archive_hash = sha256_bytes(archive)
    if actual_archive_hash != expected_archive_hash:
        raise RuntimeError(
            "Official HumanEval archive hash mismatch: "
            f"expected {expected_archive_hash}, got {actual_archive_hash}"
        )

    rows = [
        json.loads(line)
        for line in gzip.decompress(archive).decode("utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != EXPECTED_SOURCE_TASK_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_TASK_COUNT} HumanEval source tasks, found {len(rows)}"
        )
    return rows


def validate_materialized_row(row: dict[str, Any]) -> None:
    missing = REQUIRED_OUTPUT_FIELDS - set(row)
    if missing:
        raise RuntimeError(f"Materialized task {row.get('task_id')} is missing {sorted(missing)}")


def materialize(manifest_path: str | Path, output_path: str | Path) -> Path:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    rows = fetch_source(manifest)
    by_id = {row["task_id"]: row for row in rows}
    selected = manifest["tasks"]

    if len(selected) != int(manifest["task_count"]):
        raise RuntimeError("Manifest task count is inconsistent with its task list")
    if len({row["task_id"] for row in selected}) != len(selected):
        raise RuntimeError("Manifest contains duplicate task IDs")

    materialized: list[dict[str, Any]] = []
    for entry in selected:
        source = by_id.get(entry["task_id"])
        if source is None:
            raise RuntimeError(f"Manifest task missing from official source: {entry['task_id']}")

        task_hash = canonical_task_hash(source)
        test_hash = test_source_hash(source["test"])
        if task_hash != entry["task_sha256"]:
            raise RuntimeError(
                f"Task hash mismatch for {entry['task_id']}: "
                f"manifest={entry['task_sha256']} source={task_hash}"
            )
        if test_hash != entry["test_sha256"]:
            raise RuntimeError(
                f"Test hash mismatch for {entry['task_id']}: "
                f"manifest={entry['test_sha256']} source={test_hash}"
            )

        visible, hidden, assertion_count = split_assertions(source["test"])
        if assertion_count != int(entry["assertion_count"]):
            raise RuntimeError(
                f"Assertion-count mismatch for {entry['task_id']}: "
                f"manifest={entry['assertion_count']} source={assertion_count}"
            )

        row = {
            "task_id": source["task_id"],
            "task_sha256": task_hash,
            "test_sha256": test_hash,
            "prompt": strip_doctest_examples(source["prompt"]),
            "entry_point": source["entry_point"],
            "category": entry["category"],
            "difficulty": entry["difficulty"],
            "source": manifest["provenance"]["canonical_source"],
            "source_commit": manifest["provenance"]["source_commit"],
            "source_path": manifest["provenance"]["source_path"],
            "prompt_transform": "strip_doctest_examples_v1",
            "visible_tests": _build_test_source(source["entry_point"], source["test"], visible),
            "hidden_tests": _build_test_source(source["entry_point"], source["test"], hidden),
            "assertion_count": assertion_count,
        }
        validate_materialized_row(row)
        materialized.append(row)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in materialized),
        encoding="utf-8",
        newline="\n",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize the frozen EXP-001 benchmark from the pinned official HumanEval source."
    )
    parser.add_argument(
        "--manifest",
        default="benchmarks/manifests/exp001_v1.json",
    )
    parser.add_argument(
        "--output",
        default="benchmarks/programming/exp001_v1/tasks.jsonl",
    )
    args = parser.parse_args()
    print(materialize(args.manifest, args.output))


if __name__ == "__main__":
    main()
