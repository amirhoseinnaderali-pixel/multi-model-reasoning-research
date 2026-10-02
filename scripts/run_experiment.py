#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from multi_model_reasoning.budgeting import Budget
from multi_model_reasoning.collaboration.engine import CollaborationEngine
from multi_model_reasoning.collaboration.protocols import get_strategy
from multi_model_reasoning.evaluation.schema import validate_result
from multi_model_reasoning.logging.manifest import (
    git_sha,
    hash_json,
    installed_package_versions,
)
from multi_model_reasoning.models.mock import MockAdapter
from multi_model_reasoning.models.openai_adapter import OpenAIAdapter
from multi_model_reasoning.verification.mock import MockVerifier
from benchmarks.loaders.manifest import load_materialized_tasks


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


def load_role_prompts(cfg):
    return load_prompt_map(cfg["role_prompts"])


def load_condition_role_prompts(cfg):
    result = {"C5": load_prompt_map(cfg["role_prompts"])}
    if "c6_role_prompts" in cfg:
        result["C6"] = load_prompt_map(cfg["c6_role_prompts"])
    return result


def run_validation(cfg):
    adapters = {role: MockAdapter(role) for role in "ABCD"}
    records = []
    role_prompts = load_role_prompts(cfg)
    role_prompts_by_condition = load_condition_role_prompts(cfg)

    model_configs = {
        role: {
            "model_id": "mock",
            "temperature": 0,
            "top_p": 1,
            "max_tokens": 32,
            "max_input_tokens": 2048,
            "usd_per_1k_input_tokens": 0.0,
            "usd_per_1k_output_tokens": 0.0,
            "seed": 42,
        }
        for role in "ABCD"
    }

    for condition in cfg["conditions"]:
        spec = get_strategy(condition)
        budget = Budget(spec.calls_per_task, 2048, 30, 1)
        objective_verifier = MockVerifier() if spec.uses_verifier else None
        engine = CollaborationEngine(adapters, budget)

        final, outputs = engine.run(
            spec=spec,
            problem="validation problem",
            system_prompt=role_prompts["solver"]["text"],
            generation_kwargs={
                "model_configs": model_configs,
                "role_prompts": role_prompts,
                "role_prompts_by_condition": role_prompts_by_condition,
                "worst_case_seconds": 1,
            },
            verifier=objective_verifier,
        )

        record = {
            "experiment_id": cfg["experiment_id"],
            "run_id": "validation-" + uuid.uuid4().hex,
            "run_scope": "validation_only",
            "task_id": "VALIDATION_ONLY",
            "condition": condition,
            "strategy": spec.name,
            "seed": 42,
            "git_sha": git_sha(),
            "config_hash": hash_json(cfg),
            "benchmark_hash": "validation-only",
            "model_config_hash": hash_json(model_configs),
            "prompt_hash": hash_json(role_prompts_by_condition),
            "docker_digest": "NOT_EXECUTED",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "objective_verdict": "NOT_SCIENTIFIC_EVIDENCE",
            "model_calls": len(outputs),
            "output_tokens": sum(x.output_tokens for x in outputs),
            "latency_seconds": sum(x.latency_seconds for x in outputs),
            "estimated_cost_usd": 0,
            "validation_only": True,
            "python_version": sys.version,
            "platform": platform.platform(),
            "package_versions": installed_package_versions(),
            "budget_declared": {
                "max_calls": spec.calls_per_task,
                "max_output_tokens": 2048,
                "max_wall_seconds": 30,
                "max_estimated_cost_usd": 1,
            },
            "budget_consumed": budget.snapshot(),
            "aggregation_strategy": spec.aggregation,
            "execution_trace": engine.last_trace,
        }
        validate_result(record)
        records.append(record)

    output = Path("results/validation/exp001_validation.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument(
        "--mode",
        choices=["validation_only", "real"],
        default="validation_only",
    )
    args = parser.parse_args()
    cfg = load_json(args.config)

    if args.mode == "validation_only":
        return run_validation(cfg)

    if subprocess.run(
        [sys.executable, "scripts/preflight.py", "--config", args.config]
    ).returncode:
        raise SystemExit("REAL EXECUTION REFUSED")

    models = load_json(cfg["models"])["models"]
    tasks = load_materialized_tasks(cfg["materialized_tasks"])
    role_prompts = load_role_prompts(cfg)
    role_prompts_by_condition = load_condition_role_prompts(cfg)
    adapters = {role: OpenAIAdapter() for role in models}

    from multi_model_reasoning.verification.docker_verifier import CandidateVerifier

    for seed in cfg["seeds"]:
        for budget_id in cfg["budgets"]:
            budget_config = load_json(f"configs/budgets/{budget_id}.json")
            for task in tasks:
                for condition in cfg["conditions"]:
                    spec = get_strategy(condition)
                    budget = Budget(
                        budget_config["max_calls"],
                        budget_config["max_output_tokens"],
                        budget_config["max_wall_seconds"],
                        budget_config["max_estimated_cost_usd"],
                    )

                    verifier = (
                        CandidateVerifier(
                            cfg["docker_image"],
                            task["visible_tests"],
                            task["hidden_tests"],
                        )
                        if spec.uses_verifier
                        else None
                    )

                    model_configs = {
                        role: {
                            "model_id": models[role]["model_id"],
                            "temperature": models[role]["temperature"],
                            "top_p": models[role]["top_p"],
                            "max_tokens": models[role]["max_tokens"],
                            "max_input_tokens": models[role]["max_input_tokens"],
                            "usd_per_1k_input_tokens": models[role]["usd_per_1k_input_tokens"],
                            "usd_per_1k_output_tokens": models[role]["usd_per_1k_output_tokens"],
                            "seed": seed,
                        }
                        for role in models
                    }

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
                        verifier=verifier,
                    )

                    evaluator = verifier or CandidateVerifier(
                        cfg["docker_image"],
                        task["hidden_tests"],
                        task["hidden_tests"],
                    )
                    verification_result = evaluator.verify_hidden(final)

                    record = {
                        "experiment_id": cfg["experiment_id"],
                        "run_id": uuid.uuid4().hex,
                        "run_scope": "scientific_results",
                        "task_id": task["task_id"],
                        "condition": condition,
                        "strategy": spec.name,
                        "seed": seed,
                        "budget_id": budget_id,
                        "git_sha": git_sha(),
                        "config_hash": hash_json(cfg),
                        "benchmark_hash": hash_json(task),
                        "model_config_hash": hash_json(models),
                        "prompt_hash": hash_json(role_prompts_by_condition),
                        "docker_digest": cfg["docker_image"],
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "objective_verdict": verification_result.verdict.value,
                        "model_calls": len(outputs),
                        "output_tokens": sum(x.output_tokens for x in outputs),
                        "latency_seconds": sum(x.latency_seconds for x in outputs),
                        "estimated_cost_usd": budget.estimated_cost_usd,
                        "validation_only": False,
                        "python_version": sys.version,
                        "platform": platform.platform(),
                        "package_versions": installed_package_versions(),
                        "budget_declared": budget_config,
                        "budget_consumed": budget.snapshot(),
                        "aggregation_strategy": spec.aggregation,
                        "execution_trace": engine.last_trace,
                    }
                    validate_result(record)

                    output = Path("results/raw/EXP-001") / f"{record['run_id']}.json"
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(
                        json.dumps(record, indent=2) + "\n",
                        encoding="utf-8",
                    )


if __name__ == "__main__":
    main()
