#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmarks/manifests/exp001_v1.json"
TASKS_PATH = ROOT / "benchmarks/programming/exp001_v1/tasks.jsonl"

REQUIRED = {
    "task_id",
    "task_sha256",
    "test_sha256",
    "prompt",
    "entry_point",
    "visible_tests",
    "hidden_tests",
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def manifest_content_sha256(manifest: dict) -> str:
    body = {k: v for k, v in manifest.items() if k != "integrity"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected_manifest_hash = manifest["integrity"]["manifest_content_sha256"]
    actual_manifest_hash = manifest_content_sha256(manifest)
    if expected_manifest_hash != actual_manifest_hash:
        raise SystemExit(
            f"BENCHMARK FREEZE FAILED: manifest hash mismatch: "
            f"{expected_manifest_hash} != {actual_manifest_hash}"
        )

    if manifest["provenance"]["source_commit"] != "6d43fb980f9fee3c892a914eda09951f772ad10d":
        raise SystemExit("BENCHMARK FREEZE FAILED: unexpected source commit")

    lines = [
        json.loads(line)
        for line in TASKS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(lines) != 100:
        raise SystemExit(f"BENCHMARK FREEZE FAILED: expected 100 tasks, found {len(lines)}")

    manifest_ids = [item["task_id"] for item in manifest["tasks"]]
    task_ids = [item["task_id"] for item in lines]
    if task_ids != manifest_ids:
        raise SystemExit("BENCHMARK FREEZE FAILED: materialized ordering/IDs differ from manifest")
    if len(task_ids) != len(set(task_ids)):
        raise SystemExit("BENCHMARK FREEZE FAILED: duplicate task IDs")

    for row, expected in zip(lines, manifest["tasks"], strict=True):
        missing = REQUIRED - set(row)
        if missing:
            raise SystemExit(f"BENCHMARK FREEZE FAILED: {row.get('task_id')} missing {sorted(missing)}")
        if row["task_sha256"] != expected["task_sha256"]:
            raise SystemExit(f"BENCHMARK FREEZE FAILED: task hash mismatch for {row['task_id']}")
        if row["test_sha256"] != expected["test_sha256"]:
            raise SystemExit(f"BENCHMARK FREEZE FAILED: test hash mismatch for {row['task_id']}")
        if row["source_commit"] != manifest["provenance"]["source_commit"]:
            raise SystemExit(f"BENCHMARK FREEZE FAILED: wrong source commit for {row['task_id']}")
        if not row["visible_tests"].strip() or not row["hidden_tests"].strip():
            raise SystemExit(f"BENCHMARK FREEZE FAILED: empty test suite for {row['task_id']}")

    print("BENCHMARK FREEZE VERIFIED")
    print(f"tasks=100")
    print(f"manifest_sha256={expected_manifest_hash}")
    print(f"source_commit={manifest['provenance']['source_commit']}")


if __name__ == "__main__":
    validate()
