#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def canonical_hash(payload):
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def prompt_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_benchmark(manifest_path, tasks_path, errors):
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        if manifest.get("status") != "frozen":
            errors.append("benchmark manifest is not frozen")
        integrity = manifest.get("integrity", {})
        body = {k: v for k, v in manifest.items() if k != "integrity"}
        actual = canonical_hash(body)
        if integrity.get("manifest_content_sha256") != actual:
            errors.append("benchmark manifest integrity hash mismatch")

        if manifest.get("task_count") != 100:
            errors.append("EXP-001 manifest task_count must be 100")

        policy = manifest.get("selection_policy", {}).get("conditions", {})
        for condition in ("C1", "C2", "C6"):
            text = str(policy.get(condition, "")).lower()
            if "visible objective" not in text or "hidden" not in text:
                errors.append(f"{condition} visible-selection policy is not explicitly frozen")

        hidden = manifest.get("evaluation_split_policy", {}).get("hidden_test_roles", [])
        forbidden = ("candidate generation", "critique/refinement", "synthesis", "candidate ranking or selection")
        for marker in forbidden:
            if not any(marker in str(x).lower() for x in hidden):
                errors.append(f"hidden-test isolation policy missing: {marker}")

        if not Path(tasks_path).exists():
            errors.append("materialized task file missing")
            return

        rows = [json.loads(x) for x in Path(tasks_path).read_text(encoding="utf-8").splitlines() if x.strip()]
        if len(rows) != 100:
            errors.append("EXP-001 requires exactly 100 frozen tasks")

        expected = manifest.get("tasks", [])
        if len(expected) == 100:
            expected_ids = [x["task_id"] for x in expected]
            actual_ids = [x["task_id"] for x in rows]
            if actual_ids != expected_ids:
                errors.append("materialized task ordering does not match manifest")
            if len(actual_ids) != len(set(actual_ids)):
                errors.append("materialized task IDs are not unique")

            required = {"task_id", "task_sha256", "test_sha256", "prompt", "visible_tests", "hidden_tests"}
            for row, frozen in zip(rows, expected, strict=True):
                if required - set(row):
                    errors.append(f"task schema incomplete: {row.get('task_id')}")
                    break
                if row["task_sha256"] != frozen["task_sha256"]:
                    errors.append(f"task_sha256 mismatch: {row['task_id']}")
                    break
                if row["test_sha256"] != frozen["test_sha256"]:
                    errors.append(f"test_sha256 mismatch: {row['task_id']}")
                    break
    except Exception as exc:
        errors.append(f"benchmark integrity check failed: {exc}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    errors = []

    manifest = Path(cfg["benchmark_manifest"])
    tasks = Path(cfg["materialized_tasks"])
    models = Path(cfg["models"])

    if not manifest.exists():
        errors.append("benchmark manifest missing")
    if not models.exists():
        errors.append("model config missing")

    if manifest.exists():
        check_benchmark(manifest, tasks, errors)
    elif not tasks.exists():
        errors.append("materialized task file missing")

    prompt_freeze = cfg.get("prompt_freeze", {}).get("artifacts", {})
    for name, item in prompt_freeze.items():
        path = Path(item["path"])
        if not path.exists():
            errors.append(f"missing frozen prompt artifact: {name}")
        else:
            actual = prompt_sha256(path)
            if actual != item.get("sha256"):
                errors.append(f"prompt SHA-256 mismatch: {name}")
            lines = path.read_text(encoding="utf-8").splitlines()
            if not lines or not lines[0].startswith("VERSION:"):
                errors.append(f"prompt lacks explicit VERSION header: {name}")

    role_prompts = cfg.get("role_prompts", {})
    c6_role_prompts = cfg.get("c6_role_prompts", {})
    required_prompts = {"solver", "critic", "verifier", "synthesizer"}
    if required_prompts - set(role_prompts):
        errors.append("C5 role prompt mapping is incomplete")
    if {"solver", "critic", "synthesizer"} - set(c6_role_prompts):
        errors.append("C6 role prompt mapping is incomplete")

    md = json.loads(models.read_text(encoding="utf-8")) if models.exists() else {}
    for role in "ABCD":
        x = md.get("models", {}).get(role)
        if not x:
            errors.append(f"missing model role {role}")
            continue
        model_id = str(x.get("model_id", ""))
        if not model_id or model_id.startswith("REPLACE_WITH") or model_id in {"latest", "default"}:
            errors.append(f"model role {role} is not frozen")
        version = str(x.get("model_version", ""))
        if not version or version in {"REQUIRED", "latest", "default"}:
            errors.append(f"model version {role} is not frozen")
        if x.get("provider") != "openai":
            errors.append(f"model role {role} provider is not openai")
        if x.get("api_endpoint") != "https://api.openai.com/v1":
            errors.append(f"model role {role} API endpoint is not frozen to the registered OpenAI endpoint")
        if x.get("endpoint") != "chat.completions":
            errors.append(f"model role {role} endpoint must be chat.completions")
        if x.get("model_version") != x.get("model_id"):
            errors.append(f"model role {role} must use the exact frozen model identifier as model_version")
        if x.get("model_id", "").endswith("-latest") or x.get("model_id") in {"latest","default"}:
            errors.append(f"model role {role} uses an alias instead of an exact frozen identifier")
        if x.get("reasoning_effort") not in {"none","low","medium","high","xhigh"}:
            errors.append(f"reasoning_effort is not frozen for model role {role}")
        if x.get("service_tier") != "default":
            errors.append(f"service_tier must be default for model role {role}")
        for field in ("usd_per_1k_input_tokens", "usd_per_1k_output_tokens"):
            value = x.get(field)
            if not isinstance(value, (int, float)) or value <= 0:
                errors.append(f"real pricing is not frozen for model role {role}: {field}")
        if x.get("pricing_unit") != "usd_per_1k_tokens":
            errors.append(f"pricing unit is not frozen for model role {role}")
        if x.get("pricing_currency") != "USD":
            errors.append(f"pricing currency is not frozen for model role {role}")
        source = str(x.get("pricing_source", ""))
        if not source.startswith("https://developers.openai.com/api/docs/models/"):
            errors.append(f"pricing source is not an official OpenAI model page for role {role}")
        if not x.get("pricing_effective_date"):
            errors.append(f"pricing verification date missing for model role {role}")
        if x.get("max_input_tokens", 0) <= 0 or x.get("max_tokens", 0) <= 0:
            errors.append(f"token limits must be positive for model role {role}")

    docker_image = str(cfg.get("docker_image", ""))
    if not re.search(r"@sha256:[0-9a-f]{64}$", docker_image):
        errors.append("Docker image must use an immutable sha256 digest")
    if shutil.which("docker") is None:
        errors.append("Docker CLI unavailable")
    elif re.search(r"@sha256:[0-9a-f]{64}$", docker_image):
        try:
            pull = subprocess.run(
                ["docker", "pull", docker_image],
                text=True,
                capture_output=True,
                timeout=120,
            )
            if pull.returncode != 0:
                errors.append(f"Docker immutable image pull failed: {pull.stderr[-1000:]}")
            else:
                inspect = subprocess.run(
                    ["docker", "image", "inspect", docker_image, "--format", "{{json .RepoDigests}}"],
                    text=True,
                    capture_output=True,
                    timeout=20,
                )
                repo_digests = inspect.stdout.strip()
                print(f"DOCKER_REPO_DIGESTS: {repo_digests}")
                declared_digest = docker_image.split("@", 1)[1]
                if inspect.returncode != 0:
                    errors.append("Docker image inspect failed")
                else:
                    try:
                        resolved = json.loads(repo_digests)
                    except json.JSONDecodeError:
                        resolved = []
                    if not any(str(item).endswith("@"+declared_digest) for item in resolved):
                        errors.append(
                            "Docker resolved digest does not match declared digest: "
                            f"declared={declared_digest} resolved={resolved}"
                        )
        except Exception as exc:
            errors.append(f"Docker verification failed: {exc}")

    if not os.getenv("OPENAI_API_KEY"):
        errors.append("OPENAI_API_KEY unavailable")

    if cfg.get("real_execution") is not True:
        errors.append("experiment config is intentionally non-executable")
    if cfg.get("docker_source", {}).get("smoke_test_verified") is not True:
        errors.append("real Docker sandbox smoke test has not been verified")
    if not cfg.get("role_mapping"):
        errors.append("registered role mapping is missing from experiment config")

    print("READY" if not errors else "NOT READY")
    for item in errors:
        print("BLOCKED:", item)
    raise SystemExit(0 if not errors else 2)


if __name__ == "__main__":
    main()
