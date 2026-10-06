#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.loaders.manifest import load_materialized_tasks
from multi_model_reasoning.budgeting import Budget
from multi_model_reasoning.collaboration.engine import CollaborationEngine
from multi_model_reasoning.collaboration.protocols import get_strategy
from multi_model_reasoning.evaluation.schema import validate_result
from multi_model_reasoning.logging.manifest import git_sha, hash_json, installed_package_versions
from multi_model_reasoning.models.openai_adapter import OpenAIAdapter
from multi_model_reasoning.verification.docker_verifier import CandidateVerifier


def failure_from_verdict(verdict):
    value = getattr(verdict, "value", str(verdict))
    return "none" if value == "pass" else value


SMOKE_SEED = 42
SMOKE_BUDGET_ID = "B1"
SMOKE_CONDITIONS = ("C0", "C1", "C2", "C3", "C4", "C5", "C6")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_prompt_map(paths):
    return {
        role: {
            "path": path,
            "version": Path(path).read_text(encoding="utf-8").splitlines()[0].split(":", 1)[1].strip(),
            "text": Path(path).read_text(encoding="utf-8"),
        }
        for role, path in paths.items()
    }


def main():
    parser = argparse.ArgumentParser(description="One-task real EXP-001 smoke test; never a full experiment.")
    parser.add_argument("--config", default="configs/experiments/exp001_fixed_budget.json")
    args = parser.parse_args()

    cfg = load_json(args.config)
    import os
    docker_image = str(cfg.get("docker_image", ""))
    if "@sha256:" not in docker_image:
        raise SystemExit("REAL_EXECUTION_SMOKE_TEST REFUSED: Docker image is not immutable")
    if not cfg.get("docker_source", {}).get("runtime_resolution_verified"):
        raise SystemExit("REAL_EXECUTION_SMOKE_TEST REFUSED: Docker resolution is not pre-verified")
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("REAL_EXECUTION_SMOKE_TEST REFUSED: OPENAI_API_KEY unavailable")

    tasks = load_materialized_tasks(cfg["materialized_tasks"])
    if len(tasks) != 100:
        raise SystemExit("REAL_EXECUTION_SMOKE_TEST REFUSED: benchmark is not exactly 100 tasks")

    budget_cfg = load_json(f"configs/budgets/{SMOKE_BUDGET_ID}.json")
    task = tasks[0]

    role_prompts = load_prompt_map(cfg["role_prompts"])
    role_prompts_by_condition = {"C5": role_prompts}
    if "c6_role_prompts" in cfg:
        role_prompts_by_condition["C6"] = load_prompt_map(cfg["c6_role_prompts"])

    models = load_json(cfg["models"])["models"]
    model_configs = {
        role: {
            "model_id": models[role]["model_id"],
            "temperature": models[role]["temperature"],
            "top_p": models[role]["top_p"],
            "max_tokens": models[role]["max_tokens"],
            "max_input_tokens": models[role]["max_input_tokens"],
            "usd_per_1k_input_tokens": models[role]["usd_per_1k_input_tokens"],
            "usd_per_1k_output_tokens": models[role]["usd_per_1k_output_tokens"],
            "seed": SMOKE_SEED,
            "api_endpoint": models[role]["api_endpoint"],
            "reasoning_effort": models[role]["reasoning_effort"],
            "service_tier": models[role]["service_tier"],
        }
        for role in models
    }

    adapters = {role: OpenAIAdapter(api_endpoint=models[role]["api_endpoint"]) for role in models}
    records = []

    for condition in SMOKE_CONDITIONS:
        spec = get_strategy(condition)
        budget = Budget(
            budget_cfg["max_calls"],
            budget_cfg["max_output_tokens"],
            budget_cfg["max_wall_seconds"],
            budget_cfg["max_estimated_cost_usd"],
        )
        verifier = CandidateVerifier(
            cfg["docker_image"],
            task["visible_tests"],
            task["hidden_tests"],
            timeout_seconds=cfg.get("sandbox", {}).get("timeout_seconds", 10.0),
        )
        engine = CollaborationEngine(adapters, budget)
        final, outputs = engine.run(
            spec=spec,
            problem=task["prompt"],
            system_prompt=role_prompts["solver"]["text"],
            generation_kwargs={
                "model_configs": model_configs,
                "role_prompts": role_prompts,
                "role_prompts_by_condition": role_prompts_by_condition,
                "worst_case_seconds": 30,
            },
            verifier=verifier if spec.uses_verifier else None,
        )

        visible_smoke_result = verifier.verify(final, task["visible_tests"], cfg.get("sandbox", {}).get("timeout_seconds", 10.0))
        if visible_smoke_result.verdict.value == "infrastructure_failure":
            raise RuntimeError(visible_smoke_result.message)
        hidden_result = verifier.verify_hidden(final)
        record = {
            "experiment_id": cfg["experiment_id"],
            "run_id": "smoke-" + uuid.uuid4().hex,
            "run_scope": "smoke_test",
            "task_id": task["task_id"],
            "condition": condition,
            "strategy": spec.name,
            "seed": SMOKE_SEED,
            "git_sha": git_sha(),
            "config_hash": hash_json(cfg),
            "benchmark_hash": load_json(cfg["benchmark_manifest"])["integrity"]["manifest_content_sha256"],
            "task_hash": task["task_sha256"],
            "model_config_hash": hash_json({"models": models, "role_mapping": cfg.get("role_mapping", {})}),
            "prompt_hash": hash_json(role_prompts_by_condition),
            "docker_digest": cfg["docker_image"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "objective_verdict": hidden_result.verdict.value,
            "failure_classification": failure_from_verdict(hidden_result.verdict),
            "failure_message": hidden_result.message,
            "visible_smoke_verdict": visible_smoke_result.verdict.value,
            "hidden_smoke_verdict": hidden_result.verdict.value,
            "model_calls": len(outputs),
            "output_tokens": sum(x.output_tokens for x in outputs),
            "latency_seconds": sum(x.latency_seconds for x in outputs),
            "estimated_cost_usd": budget.estimated_cost_usd,
            "validation_only": False,
            "python_version": sys.version,
            "platform": platform.platform(),
            "package_versions": installed_package_versions(),
            "budget_declared": budget_cfg,
            "budget_consumed": budget.snapshot(),
            "aggregation_strategy": spec.aggregation,
            "execution_trace": engine.last_trace,
            "smoke_test_constraints": {
                "task_count": 1,
                "seed": SMOKE_SEED,
                "budget_id": SMOKE_BUDGET_ID,
                "full_exp001_forbidden": True,
            },
        }
        validate_result(record)
        records.append(record)

        out = Path("results/smoke_test/EXP-001") / f"{condition}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2) + "
", encoding="utf-8")

    summary = {
        "run_scope": "smoke_test",
        "experiment_id": cfg["experiment_id"],
        "task_id": task["task_id"],
        "conditions": list(SMOKE_CONDITIONS),
        "seed": SMOKE_SEED,
        "budget_id": SMOKE_BUDGET_ID,
        "scientific_results_path_forbidden": "results/raw/EXP-001",
        "records": len(records),
    }
    Path("results/smoke_test/EXP-001/summary.json").write_text(
        json.dumps(summary, indent=2) + "
",
        encoding="utf-8",
    )
    print("REAL_EXECUTION_SMOKE_TEST COMPLETE")


if __name__ == "__main__":
    main()
