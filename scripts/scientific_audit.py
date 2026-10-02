#!/usr/bin/env python3
import json,sys
from pathlib import Path

sys.path.insert(0,"src")
from multi_model_reasoning.collaboration.protocols import SPECS

def main():
    errors=[]
    blockers=[]
    cfg=json.loads(Path("configs/experiments/exp001_fixed_budget.json").read_text())

    if set(cfg["conditions"])!=set(SPECS):
        errors.append("EXP-001 does not enumerate C0-C6 exactly")
    if len(cfg.get("seeds",[]))<3:
        errors.append("fewer than three seeds")
    if len(cfg.get("budgets",[]))<4:
        errors.append("fewer than four budgets")
    if not Path(cfg["prompt"]).exists():
        errors.append("solver prompt missing")

    role_prompts=cfg.get("role_prompts",{})
    required={"solver","critic","verifier","synthesizer"}
    if required-set(role_prompts):
        errors.append("C5 role prompt mapping incomplete")
    for role in required & set(role_prompts):
        path=Path(role_prompts[role])
        if not path.exists():
            errors.append(f"C5 role prompt missing: {role}")
        elif not path.read_text().splitlines() or not path.read_text().splitlines()[0].startswith("VERSION:"):
            errors.append(f"C5 role prompt missing VERSION header: {role}")

    if not SPECS["C1"].uses_verifier or SPECS["C1"].aggregation!="visible_objective_selection":
        errors.append("C1 does not use visible objective candidate selection")
    if not SPECS["C2"].uses_verifier or SPECS["C2"].aggregation!="visible_objective_selection":
        errors.append("C2 does not use visible objective candidate selection")
    if SPECS["C5"].semantic_roles!=("solver","critic","verifier","synthesizer"):
        errors.append("C5 semantic role sequence is not explicit")

    m=json.loads(Path(cfg["benchmark_manifest"]).read_text())
    if m.get("status","").startswith("provenance_manifest_only"):
        blockers.append("benchmark task materialization pending")
    if cfg.get("real_execution") is not True:
        blockers.append("real_execution is intentionally disabled")
    if "REPLACE_WITH" in cfg.get("docker_image",""):
        blockers.append("Docker digest not frozen")

    for e in errors:
        print("FAIL:",e)
    if errors:
        raise SystemExit(1)

    if blockers:
        print("AUDIT: FAIL-CLOSED")
        for b in blockers:
            print("BLOCKED:",b)
        raise SystemExit(2)

    print("AUDIT: PASS")

if __name__=="__main__":
    main()
