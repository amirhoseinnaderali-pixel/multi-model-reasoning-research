#!/usr/bin/env python3
from __future__ import annotations

import gzip
import hashlib
import json
import urllib.request
from pathlib import Path


EXPECTED_SOURCE_TASK_COUNT = 164
SOURCE_COMMIT = "6d43fb980f9fee3c892a914eda09951f772ad10d"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_task_hash(task: dict) -> str:
    payload = {
        "task_id": task["task_id"],
        "prompt": task["prompt"],
        "entry_point": task["entry_point"],
    }
    return sha256_bytes(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def fetch_source(manifest: dict) -> list[dict]:
    provenance = manifest["provenance"]
    if provenance["source_commit"] != SOURCE_COMMIT:
        raise RuntimeError("Pinned source commit does not match EXP-001 provenance")
    url = (
        f"https://raw.githubusercontent.com/openai/human-eval/"
        f"{SOURCE_COMMIT}/data/HumanEval.jsonl.gz"
    )
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "multi-model-reasoning-research/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        archive = response.read()

    actual_archive_hash = sha256_bytes(archive)
    expected_archive_hash = provenance["source_archive_sha256"]
    if actual_archive_hash != expected_archive_hash:
        raise RuntimeError(
            "Pinned HumanEval archive hash mismatch: "
            f"expected {expected_archive_hash}, got {actual_archive_hash}"
        )

    rows = [
        json.loads(line)
        for line in gzip.decompress(archive).decode("utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != EXPECTED_SOURCE_TASK_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_TASK_COUNT} HumanEval source tasks, got {len(rows)}"
        )
    return rows


def main() -> None:
    manifest_path = Path("benchmarks/manifests/exp001_v1.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = fetch_source(manifest)
    by_id = {row["task_id"]: row for row in rows}

    selected = manifest["tasks"]
    if len(selected) != manifest["task_count"] or manifest["task_count"] != 100:
        raise RuntimeError("EXP-001 manifest must select exactly 100 tasks")
    if len({row["task_id"] for row in selected}) != len(selected):
        raise RuntimeError("Manifest contains duplicate task IDs")

    changes = []
    for entry in selected:
        source = by_id.get(entry["task_id"])
        if source is None:
            raise RuntimeError(f"Manifest task missing from pinned source: {entry['task_id']}")

        actual_task_hash = canonical_task_hash(source)
        actual_test_hash = sha256_bytes(source["test"].encode("utf-8"))

        if (
            entry["task_sha256"] != actual_task_hash
            or entry["test_sha256"] != actual_test_hash
        ):
            changes.append({
                "task_id": entry["task_id"],
                "old_task_sha256": entry["task_sha256"],
                "new_task_sha256": actual_task_hash,
                "old_test_sha256": entry["test_sha256"],
                "new_test_sha256": actual_test_hash,
            })
            entry["task_sha256"] = actual_task_hash
            entry["test_sha256"] = actual_test_hash

    manifest["hash_verification"] = {
        "algorithm": "sha256",
        "task_hash_payload": ["task_id", "prompt", "entry_point"],
        "test_hash_payload": "raw source test string",
        "recomputed_from_exact_pinned_source": True,
        "source_task_count": EXPECTED_SOURCE_TASK_COUNT,
        "changed_task_count": len(changes),
    }

    body = {k: v for k, v in manifest.items() if k != "integrity"}
    manifest["integrity"] = {
        "hash_algorithm": "sha256",
        "manifest_content_sha256": sha256_bytes(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ),
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(json.dumps({
        "source_commit": SOURCE_COMMIT,
        "source_task_count": EXPECTED_SOURCE_TASK_COUNT,
        "selected_task_count": len(selected),
        "changed_task_count": len(changes),
        "changed_task_ids": [x["task_id"] for x in changes],
    }, indent=2))


if __name__ == "__main__":
    main()
