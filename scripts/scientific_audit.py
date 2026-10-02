#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from multi_model_reasoning.collaboration.protocols import SPECS


def main():
    errors = []
    blockers = []
    cfg = json.loads(Path("configs/experiments/exp001_fixed_budget.json").read_text())
    manifest = json.loads(Path(cfg["benchmark_manifest"]).read_text())

    if set(cfg["conditions"]) != set(SPECS):
        errors.append("EXP-001 does not enumerate C0-C6 exactly")
    if len(cfg.get("seeds", [])) < 3:
        errors.append("fewer than three seeds")
    if len(cfg.get("budgets", [])) < 4:
        errors.append("fewer than four budgets")
    if not Path(cfg["prompt"]).exists():
        errors.append("solver prompt missing")

    required_c5 = {"solver", "critic", "verifier", "synthesizer"}
    role_prompts = cfg.get("role_prompts", {})
    if required_c5 - set(role_prompts):
        errors.append("C5 role prompt mapping incomplete")
    for role in required_c5 & set(role_prompts):
        path = Path(role_prompts[role])
        if not path.exists():
            errors.append(f"C5 role prompt missing: {role}")
        else:
            lines = path.read_text().splitlines()
            if not lines or not lines[0].startswith("VERSION:"):
                errors.append(f"C5 role prompt missing VERSION header: {role}")

    c6 = SPECS["C6"]
    c2 = SPECS["C2"]
    c3 = SPECS["C3"]
    c4 = SPECS["C4"]
    c5 = SPECS["C5"]

    if c2.model_pool != ("A", "B", "C") or c2.semantic_roles != ("solver", "solver", "solver"):
        errors.append("C2 must remain independent multi-model solver generation")
    if c3.model_pool != ("A", "B") or c3.rounds != 2 or c3.calls_per_task != 3 or c3.semantic_roles != ("solver", "critic"):
        errors.append("C3 debate/critique protocol changed")
    if c4.model_pool != ("A", "B", "C"):
        errors.append("C4 model pool changed")
    if c5.model_pool != ("A", "B", "C", "D") or c5.semantic_roles != ("solver", "critic", "verifier", "synthesizer"):
        errors.append("C5 role-specialized protocol changed")

    c6_prompts = cfg.get("c6_role_prompts", {})
    required_c6 = {"solver", "critic", "synthesizer"}
    if c6.semantic_roles != ("solver", "critic", "synthesizer"):
        errors.append("C6 semantic roles are not solver/critic/synthesizer")
    if c6.rounds != 3 or c6.calls_per_task != 3:
        errors.append("C6 must have exactly three collaborative model rounds/calls")
    if not c6.uses_verifier:
        errors.append("C6 must use independent objective verification")
    if c6.aggregation != "sequential_refinement_visible_selection":
        errors.append("C6 must use sequential refinement plus visible objective selection")
    if c6.model_pool != ("A", "B", "C"):
        errors.append("C6 model pool must be A/B/C")
    if required_c6 - set(c6_prompts):
        errors.append("C6 role prompt mapping incomplete")

    for role in required_c6 & set(c6_prompts):
        path = Path(c6_prompts[role])
        if not path.exists():
            errors.append(f"C6 role prompt missing: {role}")
        else:
            lines = path.read_text().splitlines()
            if not lines or not lines[0].startswith("VERSION: c6-"):
                errors.append(f"C6 role prompt missing C6 VERSION header: {role}")

    if c6.semantic_roles == c2.semantic_roles and c6.description == c2.description:
        errors.append("C6 is structurally indistinguishable from C2")

    selection = cfg.get("selection_policy", {})
    manifest_selection = manifest.get("selection_policy", {}).get("conditions", {})
    for condition in ("C1", "C2", "C6"):
        policy = str(selection.get(condition, "")).lower()
        frozen = str(manifest_selection.get(condition, "")).lower()
        if "visible objective" not in policy or "hidden tests reserved" not in policy:
            errors.append(f"{condition} config selection policy is not explicit")
        if "visible objective" not in frozen or "hidden" not in frozen:
            errors.append(f"{condition} benchmark manifest selection policy is not frozen")

    hidden_roles = [
        str(x).lower()
        for x in manifest.get("evaluation_split_policy", {}).get("hidden_test_roles", [])
    ]
    for required in ("candidate generation", "critique/refinement", "synthesis", "candidate ranking or selection"):
        if not any(required in item for item in hidden_roles):
            errors.append(f"hidden-test isolation missing for {required}")
    if not any("reserved for final evaluation" in item for item in hidden_roles):
        errors.append("hidden tests are not explicitly reserved for final evaluation")

    if manifest.get("provenance", {}).get("source_commit") != "6d43fb980f9fee3c892a914eda09951f772ad10d":
        errors.append("benchmark source commit changed")
    if manifest.get("task_count") != 100:
        errors.append("benchmark task count changed from 100")

    if cfg.get("real_execution") is not True:
        blockers.append("real_execution is intentionally disabled")
    if "REPLACE_WITH" in str(cfg.get("docker_image", "")):
        blockers.append("Docker digest not frozen")
    if manifest.get("status") != "frozen":
        blockers.append("benchmark manifest is not frozen")
    if not Path(cfg["materialized_tasks"]).exists():
        blockers.append("benchmark task artifact is not materialized")
    models = json.loads(Path(cfg["models"]).read_text())["models"]
    for role in "ABCD":
        model = models.get(role, {})
        if str(model.get("model_id", "")).startswith("REPLACE_WITH") or model.get("model_version") in (None, "REQUIRED"):
            blockers.append(f"model role {role} is not frozen")
        if not model.get("pricing_source") or model.get("pricing_effective_date") is None:
            blockers.append(f"pricing metadata for model role {role} is not frozen")

    for error in errors:
        print("FAIL:", error)
    if errors:
        raise SystemExit(1)

    if blockers:
        print("AUDIT: FAIL-CLOSED")
        for blocker in blockers:
            print("BLOCKED:", blocker)
        raise SystemExit(2)

    print("AUDIT: PASS")


if __name__ == "__main__":
    main()
