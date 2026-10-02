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

from multi_model_reasoning.budgeting import Budget, BudgetExceeded
from multi_model_reasoning.collaboration.engine import CollaborationEngine, _classify_model_failure
from multi_model_reasoning.collaboration.protocols import get_strategy
from multi_model_reasoning.evaluation.schema import validate_result
from multi_model_reasoning.logging.manifest import git_sha, hash_json, installed_package_versions
from multi_model_reasoning.models.mock import MockAdapter
from multi_model_reasoning.models.openai_adapter import OpenAIAdapter
from multi_model_reasoning.verification.mock import MockVerifier
from multi_model_reasoning.verification.docker_verifier import CandidateVerifier
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


def benchmark_metadata(cfg):
    manifest = load_json(cfg["benchmark_manifest"])
    return manifest["integrity"]["manifest_content_sha256"]


def role_model_configs(models, seed):
    return {
        role: {
            "model_id": models[role]["model_id"],
            "temperature": models[role]["temperature"],
            "top_p": models[role]["top_p"],
            "max_tokens": models[role]["max_tokens"],
            "max_input_tokens": models[role]["max_input_tokens"],
            "usd_per_1k_input_tokens": models[role]["usd_per_1k_input_tokens"],
            "usd_per_1k_output_tokens": models[role]["usd_per_1k_output_tokens"],
            "seed": seed,
            "api_endpoint": models[role]["api_endpoint"],
            "reasoning_effort": models[role]["reasoning_effort"],
            "service_tier": models[role]["service_tier"],
        }
        for role in models
    }


def failure_from_exception(exc):
    if isinstance(exc, BudgetExceeded):
        return "budget_exceeded"
    text = str(exc).lower()
    if "docker" in text or "sandbox" in text:
        return "infrastructure_failure"
    if "api key" in text or "authentication" in text or "unauthorized" in text:
        return "credential_failure"
    if "timeout" in text or "timed out" in text:
        return "timeout"
    return "protocol_failure"


def failure_from_verdict(verdict):
    value = getattr(verdict, "value", str(verdict))
    return "none" if value == "pass" else value


def base_record(*, cfg, models, task, benchmark_hash, condition, spec, seed, budget_id, budget,
                model_configs, role_prompts_by_condition, docker_digest, run_scope, run_id,
                objective_verdict, failure_classification, failure_message, outputs, trace):
    return {
        "experiment_id": cfg["experiment_id"],
        "run_id": run_id,
        "run_scope": run_scope,
        "task_id": task.get("task_id", "VALIDATION_ONLY"),
        "condition": condition,
        "strategy": spec.name,
        "seed": seed,
        "git_sha": git_sha(),
        "config_hash": hash_json(cfg),
        "benchmark_hash": benchmark_hash,
        "task_hash": task.get("task_sha256", "validation-only"),
        "model_config_hash": hash_json({"models": models, "role_mapping": cfg.get("role_mapping", {})}),
        "prompt_hash": hash_json(role_prompts_by_condition),
        "docker_digest": docker_digest,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "objective_verdict": objective_verdict,
        "failure_classification": failure_classification,
        "failure_message": failure_message,
        "model_calls": len(outputs),
        "output_tokens": sum(x.output_tokens for x in outputs),
        "latency_seconds": sum(x.latency_seconds for x in outputs),
        "estimated_cost_usd": budget.estimated_cost_usd,
        "validation_only": run_scope == "validation_only",
        "python_version": sys.version,
        "platform": platform.platform(),
        "package_versions": installed_package_versions(),
        "budget_declared": ({
            "max_calls": budget.max_calls,
            "max_output_tokens": budget.max_output_tokens,
            "max_wall_seconds": budget.max_wall_seconds,
            "max_estimated_cost_usd": budget.max_estimated_cost_usd,
        } if run_scope == "validation_only" else load_json(f"configs/budgets/{budget_id}.json")),
        "budget_consumed": budget.snapshot(),
        "aggregation_strategy": spec.aggregation,
        "execution_trace": trace,
    }


def run_validation(cfg):
    adapters = {role: MockAdapter(role) for role in "ABCD"}
    records = []
    role_prompts = load_role_prompts(cfg)
    role_prompts_by_condition = load_condition_role_prompts(cfg)
    models = {
        role: {
            "provider": "mock",
            "model_id": "mock",
            "model_version": "validation-only",
            "api_endpoint": "NOT_EXECUTED",
            "endpoint": "chat.completions",
            "temperature": 0.0,
            "top_p": 1.0,
            "reasoning_effort": "none",
            "service_tier": "default",
            "max_tokens": 32,
            "max_input_tokens": 2048,
            "usd_per_1k_input_tokens": 0.0,
            "usd_per_1k_output_tokens": 0.0,
            "seed": 42,
        } for role in "ABCD"
    }
    task = {"task_id": "VALIDATION_ONLY", "task_sha256": "validation-only"}

    for condition in cfg["conditions"]:
        spec = get_strategy(condition)
        budget = Budget(spec.calls_per_task, 2048, 30, 1)
        verifier = MockVerifier() if spec.uses_verifier else None
        engine = CollaborationEngine(adapters, budget)
        final, outputs = engine.run(
            spec=spec,
            problem="validation problem",
            system_prompt=role_prompts["solver"]["text"],
            generation_kwargs={
                "model_configs": models,
                "role_prompts": role_prompts,
                "role_prompts_by_condition": role_prompts_by_condition,
                "worst_case_seconds": 1,
            },
            verifier=verifier,
        )
        record = base_record(
            cfg=cfg, models=models, task=task, benchmark_hash="validation-only",
            condition=condition, spec=spec, seed=42, budget_id="validation",
            budget=budget, model_configs=models, role_prompts_by_condition=role_prompts_by_condition,
            docker_digest="NOT_EXECUTED", run_scope="validation_only",
            run_id="validation-" + uuid.uuid4().hex,
            objective_verdict="NOT_SCIENTIFIC_EVIDENCE",
            failure_classification="none", failure_message="",
            outputs=outputs, trace=engine.last_trace,
        )
        validate_result(record)
        records.append(record)

    output = Path("results/validation/exp001_validation.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(output)


def run_real(cfg):
    if subprocess.run([sys.executable, "scripts/preflight.py", "--config", args.config]).returncode:
        raise SystemExit("REAL EXECUTION REFUSED")

    models = load_json(cfg["models"])["models"]
    tasks = load_materialized_tasks(cfg["materialized_tasks"])
    benchmark_hash = benchmark_metadata(cfg)
    role_prompts = load_role_prompts(cfg)
    role_prompts_by_condition = load_condition_role_prompts(cfg)
    adapters = {role: OpenAIAdapter(api_endpoint=models[role]["api_endpoint"]) for role in models}
    records_path = Path("results/raw/EXP-001")
    records_path.mkdir(parents=True, exist_ok=True)

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
                    verifier = CandidateVerifier(
                        cfg["docker_image"],
                        task["visible_tests"],
                        task["hidden_tests"],
                        timeout_seconds=cfg.get("sandbox", {}).get("timeout_seconds", 10.0),
                    )
                    model_configs = role_model_configs(models, seed)
                    engine = CollaborationEngine(adapters, budget)

                    outputs = []
                    try:
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
                        verification_result = verifier.verify_hidden(final)
                        failure_classification = failure_from_verdict(verification_result.verdict)
                        failure_message = verification_result.message
                        objective_verdict = verification_result.verdict.value
                    except Exception as exc:
                        objective_verdict = "not_evaluated"
                        failure_classification = (
                            engine.last_trace[-1].get("failure_classification")
                            if engine.last_trace and engine.last_trace[-1].get("event") == "model_call_failure"
                            else failure_from_exception(exc)
                        )
                        failure_message = str(exc)[-4000:]

                    record = base_record(
                        cfg=cfg, models=models, task=task, benchmark_hash=benchmark_hash,
                        condition=condition, spec=spec, seed=seed, budget_id=budget_id,
                        budget=budget, model_configs=model_configs,
                        role_prompts_by_condition=role_prompts_by_condition,
                        docker_digest=cfg["docker_image"], run_scope="scientific_results",
                        run_id=uuid.uuid4().hex, objective_verdict=objective_verdict,
                        failure_classification=failure_classification,
                        failure_message=failure_message, outputs=outputs,
                        trace=engine.last_trace,
                    )
                    record["budget_declared"] = budget_config
                    validate_result(record)
                    (records_path / f"{record['run_id']}.json").write_text(
                        json.dumps(record, indent=2) + "\n", encoding="utf-8"
                    )


def main():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--mode", choices=["validation_only","real"], default="validation_only")
    args = parser.parse_args()
    cfg = load_json(args.config)
    if args.mode == "validation_only":
        run_validation(cfg)
    else:
        run_real(cfg)


if __name__ == "__main__":
    main()
