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
from typing import Any, Iterable

# EXP-001 freeze materializer: canonical HumanEval source only; no alternate dataset fallback.\nEXPECTED_SOURCE_TASK_COUNT = 164
REQUIRED_OUTPUT_FIELDS = {
    "task_id",
    "task_sha256",
    "test_sha256",
    "prompt",
    "entry_point",
    "visible_tests",
    "hidden_tests",
}
ACTIVE_ASSERTIONS_NAME = "_MMR_ACTIVE_ASSERT_IDS"


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


def _check_function(tree: ast.Module) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "check":
            return node
    raise ValueError("Test source does not define check(candidate)")


def _iter_asserts(node: ast.AST) -> Iterable[ast.Assert]:
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.Assert):
            yield child
        yield from _iter_asserts(child)


def _assert_nodes(test_source: str) -> list[ast.Assert]:
    return list(_iter_asserts(_check_function(ast.parse(test_source))))


class _AssertGateTransformer(ast.NodeTransformer):
    def __init__(self) -> None:
        self.next_id = 0

    def visit_Assert(self, node: ast.Assert) -> ast.If:
        node = self.generic_visit(node)
        assert isinstance(node, ast.Assert)

        assert_id = self.next_id
        self.next_id += 1

        gate = ast.If(
            test=ast.Compare(
                left=ast.Constant(value=assert_id),
                ops=[ast.In()],
                comparators=[ast.Name(id=ACTIVE_ASSERTIONS_NAME, ctx=ast.Load())],
            ),
            body=[node],
            orelse=[],
        )
        return ast.copy_location(gate, node)


def _module_setup(tree: ast.Module) -> str:
    setup_nodes = [
        node for node in tree.body
        if not (isinstance(node, ast.FunctionDef) and node.name == "check")
    ]
    if not setup_nodes:
        return ""
    return "\n\n".join(ast.unparse(node) for node in setup_nodes).rstrip()


def _build_test_source(
    entry_point: str,
    test_source: str,
    active_assert_ids: list[int],
) -> str:
    tree = ast.parse(test_source)
    check = _check_function(tree)
    assert_count = len(list(_iter_asserts(check)))

    if not active_assert_ids:
        raise ValueError("An evaluation suite cannot contain zero active assertions")
    if any(i < 0 or i >= assert_count for i in active_assert_ids):
        raise ValueError("Active assertion ID is outside the source assertion range")

    transformed = _AssertGateTransformer().visit(tree)
    ast.fix_missing_locations(transformed)
    setup = _module_setup(transformed)
    check_fn = _check_function(transformed)

    # Keep all original control flow and helper/setup statements intact. Only
    # assertion execution is gated by the frozen visible/hidden assertion IDs.
    parts: list[str] = [
        f"{ACTIVE_ASSERTIONS_NAME} = {sorted(active_assert_ids)!r}",
    ]
    if setup:
        parts.append(setup)
    parts.append(ast.unparse(check_fn))
    parts.append(f"from candidate import {entry_point} as candidate")
    parts.append("check(candidate)")
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


def materialize(manifest_path: str | Path, output_path: str | Path) -> Path:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    rows = fetch_source(manifest)
    by_id = {row["task_id"]: row for row in rows}
    selected = manifest["tasks"]

    if len(selected) != int(manifest["task_count"]) or int(manifest["task_count"]) != 100:
        raise RuntimeError("EXP-001 requires exactly 100 selected tasks")
    if len({row["task_id"] for row in selected}) != len(selected):
        raise RuntimeError("Manifest contains duplicate task IDs")

    materialized: list[dict[str, Any]] = []
    for entry in selected:
        source = by_id.get(entry["task_id"])
        if source is None:
            raise RuntimeError(
                f"Manifest task missing from official source: {entry['task_id']}"
            )

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

        assert_count = len(_assert_nodes(source["test"]))
        if assert_count < 2:
            raise RuntimeError(
                f"Task {entry['task_id']} has fewer than two executable assertions"
            )

        cut = (assert_count + 1) // 2
        visible_ids = list(range(cut))
        hidden_ids = list(range(cut, assert_count))

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
            "visible_tests": _build_test_source(
                source["entry_point"], source["test"], visible_ids
            ),
            "hidden_tests": _build_test_source(
                source["entry_point"], source["test"], hidden_ids
            ),
            "assertion_count": assert_count,
            "assertion_split": {
                "visible_assertion_ids": visible_ids,
                "hidden_assertion_ids": hidden_ids,
                "split_policy": "static_assert_source_order_v1",
            },
        }
        missing = REQUIRED_OUTPUT_FIELDS - set(row)
        if missing:
            raise RuntimeError(
                f"Materialized task {row['task_id']} missing {sorted(missing)}"
            )
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
