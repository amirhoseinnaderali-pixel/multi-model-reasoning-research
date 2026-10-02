#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,uuid,platform,sys,subprocess
from pathlib import Path

sys.path.insert(0,"src")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from multi_model_reasoning.budgeting import Budget
from multi_model_reasoning.collaboration.protocols import get_strategy
from multi_model_reasoning.collaboration.engine import CollaborationEngine
from multi_model_reasoning.models.mock import MockAdapter
from multi_model_reasoning.models.openai_adapter import OpenAIAdapter
from multi_model_reasoning.evaluation.schema import validate_result
from multi_model_reasoning.logging.manifest import git_sha,hash_json
from multi_model_reasoning.verification.mock import MockVerifier
from benchmarks.loaders.manifest import load_materialized_tasks

def load_json(p):
    return json.loads(Path(p).read_text())

def load_role_prompts(cfg):
    paths=cfg["role_prompts"]
    return {
        role: {
            "path": path,
            "version": Path(path).read_text().splitlines()[0].split(":",1)[1].strip(),
            "text": Path(path).read_text(),
        }
        for role, path in paths.items()
    }

def run_validation(cfg):
    adapters={r:MockAdapter(r) for r in "ABCD"}
    records=[]
    role_prompts=load_role_prompts(cfg)
    model_configs={
        r:{
            "model_id":"mock",
            "temperature":0,
            "top_p":1,
            "max_tokens":32,
            "max_input_tokens":2048,
            "usd_per_1k_input_tokens":0.0,
            "usd_per_1k_output_tokens":0.0,
            "seed":42,
        }
        for r in "ABCD"
    }

    for condition in cfg["conditions"]:
        spec=get_strategy(condition)
        budget=Budget(spec.calls_per_task,2048,30,1)
        objective_verifier=MockVerifier() if spec.uses_verifier else None
        engine=CollaborationEngine(adapters,budget)
        final,outputs=engine.run(
            spec=spec,
            problem="validation problem",
            system_prompt=role_prompts["solver"]["text"],
            generation_kwargs={
                "model_configs":model_configs,
                "role_prompts":role_prompts,
                "worst_case_seconds":1,
            },
            verifier=objective_verifier,
        )
        r={
            "experiment_id":cfg["experiment_id"],
            "run_id":"validation-"+uuid.uuid4().hex,
            "task_id":"VALIDATION_ONLY",
            "condition":condition,
            "seed":42,
            "git_sha":git_sha(),
            "config_hash":hash_json(cfg),
            "benchmark_hash":"validation-only",
            "model_config_hash":hash_json(model_configs),
            "prompt_hash":hash_json(role_prompts),
            "objective_verdict":"NOT_SCIENTIFIC_EVIDENCE",
            "model_calls":len(outputs),
            "output_tokens":sum(x.output_tokens for x in outputs),
            "latency_seconds":sum(x.latency_seconds for x in outputs),
            "estimated_cost_usd":0,
            "validation_only":True,
            "python_version":sys.version,
            "platform":platform.platform(),
            "budget_declared":{
                "max_calls":spec.calls_per_task,
                "max_output_tokens":2048,
                "max_wall_seconds":30,
                "max_estimated_cost_usd":1,
            },
            "budget_consumed":budget.snapshot(),
            "aggregation_strategy":spec.aggregation,
            "execution_trace":engine.last_trace,
        }
        validate_result(r)
        records.append(r)

    out=Path("results/validation/exp001_validation.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(records,indent=2)+"\n")
    print(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True)
    ap.add_argument("--mode",choices=["validation_only","real"],default="validation_only")
    a=ap.parse_args()
    cfg=load_json(a.config)

    if a.mode=="validation_only":
        return run_validation(cfg)

    if subprocess.run(
        [sys.executable,"scripts/preflight.py","--config",a.config]
    ).returncode:
        raise SystemExit("REAL EXECUTION REFUSED")

    models=load_json(cfg["models"])["models"]
    tasks=load_materialized_tasks(cfg["materialized_tasks"])
    role_prompts=load_role_prompts(cfg)
    adapters={r:OpenAIAdapter() for r in models}

    from multi_model_reasoning.verification.docker_verifier import CandidateVerifier

    for seed in cfg["seeds"]:
        for budget_id in cfg["budgets"]:
            bc=load_json(f"configs/budgets/{budget_id}.json")
            for task in tasks:
                for condition in cfg["conditions"]:
                    spec=get_strategy(condition)
                    budget=Budget(
                        bc["max_calls"],
                        bc["max_output_tokens"],
                        bc["max_wall_seconds"],
                        bc["max_estimated_cost_usd"],
                    )

                    verifier=(
                        CandidateVerifier(
                            cfg["docker_image"],
                            task["visible_tests"],
                            task["hidden_tests"],
                        )
                        if spec.uses_verifier else None
                    )

                    model_configs={
                        r:{
                            "model_id":models[r]["model_id"],
                            "temperature":models[r]["temperature"],
                            "top_p":models[r]["top_p"],
                            "max_tokens":models[r]["max_tokens"],
                            "max_input_tokens":models[r]["max_input_tokens"],
                            "usd_per_1k_input_tokens":models[r]["usd_per_1k_input_tokens"],
                            "usd_per_1k_output_tokens":models[r]["usd_per_1k_output_tokens"],
                            "seed":seed,
                        }
                        for r in models
                    }

                    engine=CollaborationEngine(adapters,budget)
                    final,outputs=engine.run(
                        spec=spec,
                        problem=task["prompt"],
                        system_prompt=role_prompts["solver"]["text"],
                        generation_kwargs={
                            "model_configs":model_configs,
                            "role_prompts":role_prompts,
                            "worst_case_seconds":30,
                        },
                        verifier=verifier,
                    )

                    evaluator=verifier or CandidateVerifier(
                        cfg["docker_image"],
                        task["hidden_tests"],
                        task["hidden_tests"],
                    )
                    vr=evaluator.verify_hidden(final)

                    rec={
                        "experiment_id":cfg["experiment_id"],
                        "run_id":uuid.uuid4().hex,
                        "task_id":task["task_id"],
                        "condition":condition,
                        "seed":seed,
                        "budget_id":budget_id,
                        "git_sha":git_sha(),
                        "config_hash":hash_json(cfg),
                        "benchmark_hash":hash_json(task),
                        "model_config_hash":hash_json(models),
                        "prompt_hash":hash_json(role_prompts),
                        "objective_verdict":vr.verdict.value,
                        "model_calls":len(outputs),
                        "output_tokens":sum(x.output_tokens for x in outputs),
                        "latency_seconds":sum(x.latency_seconds for x in outputs),
                        "estimated_cost_usd":budget.estimated_cost_usd,
                        "validation_only":False,
                        "python_version":sys.version,
                        "platform":platform.platform(),
                        "budget_declared":bc,
                        "budget_consumed":budget.snapshot(),
                        "aggregation_strategy":spec.aggregation,
                        "execution_trace":engine.last_trace,
                    }
                    validate_result(rec)

                    out=Path("results/raw/EXP-001")/f"{rec['run_id']}.json"
                    out.parent.mkdir(parents=True,exist_ok=True)
                    out.write_text(json.dumps(rec,indent=2)+"\n")

if __name__=="__main__":
    main()
