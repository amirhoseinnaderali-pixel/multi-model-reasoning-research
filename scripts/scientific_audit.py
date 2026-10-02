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
    required_c5={"solver","critic","verifier","synthesizer"}
    if required_c5-set(role_prompts):
        errors.append("C5 role prompt mapping incomplete")
    for role in required_c5 & set(role_prompts):
        path=Path(role_prompts[role])
        if not path.exists():
            errors.append(f"C5 role prompt missing: {role}")
        elif not path.read_text().splitlines() or not path.read_text().splitlines()[0].startswith("VERSION:"):
            errors.append(f"C5 role prompt missing VERSION header: {role}")

    c6=SPECS["C6"]
    c2=SPECS["C2"]
    required_c6={"solver","critic","synthesizer"}
    c6_prompt_paths=cfg.get("c6_role_prompts",{})
    if c6.semantic_roles != ("solver","critic","synthesizer"):
        errors.append("C6 semantic roles are not solver/critic/synthesizer")
    if c6.rounds != 3:
        errors.append("C6 must have exactly three collaborative model rounds")
    if not c6.uses_verifier:
        errors.append("C6 must use independent objective verification")
    if c6.aggregation != "sequential_refinement_visible_selection":
        errors.append("C6 must use sequential refinement plus visible objective selection")
    if required_c6-set(c6_prompt_paths):
        errors.append("C6 role prompt mapping incomplete")
    for role in required_c6 & set(c6_prompt_paths):
        path=Path(c6_prompt_paths[role])
        if not path.exists():
            errors.append(f"C6 role prompt missing: {role}")
        else:
            lines=path.read_text().splitlines()
            if not lines or not lines[0].startswith("VERSION:"):
                errors.append(f"C6 role prompt missing VERSION header: {role}")
            if not lines or not lines[0].lower().startswith("version: c6-"):
                errors.append(f"C6 role prompt is not explicitly C6-scoped: {role}")

    if c6.semantic_roles == c2.semantic_roles and c6.description == c2.description:
        errors.append("C6 is structurally indistinguishable from C2")
    if c6.model_pool != ("A","B","C"):
        errors.append("C6 model pool must be A/B/C")
    if c2.model_pool != ("A","B","C"):
        errors.append("C2 model pool must remain A/B/C")
    if c2.semantic_roles != ("solver","solver","solver"):
        errors.append("C2 must remain independent solver generation")
    if c6.calls_per_task != 3:
        errors.append("C6 must make exactly three model calls")
    if c6.name != "collaborative_refinement_verified":
        errors.append("C6 strategy name changed unexpectedly")

    selection=cfg.get("selection_policy",{})
    if "C6" not in selection:
        errors.append("C6 visible-selection policy missing")
    elif "visible objective" not in selection["C6"].lower() or "hidden tests reserved" not in selection["C6"].lower():
        errors.append("C6 selection policy does not explicitly reserve hidden tests")

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
