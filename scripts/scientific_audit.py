#!/usr/bin/env python3
import json,sys
from pathlib import Path
sys.path.insert(0,"src")
from multi_model_reasoning.collaboration.protocols import SPECS
def main():
    errors=[]; blockers=[]; cfg=json.loads(Path("configs/experiments/exp001_fixed_budget.json").read_text())
    if set(cfg["conditions"])!=set(SPECS):errors.append("EXP-001 does not enumerate C0-C6 exactly")
    if len(cfg.get("seeds",[]))<3:errors.append("fewer than three seeds")
    if len(cfg.get("budgets",[]))<4:errors.append("fewer than four budgets")
    if not Path(cfg["prompt"]).exists():errors.append("versioned prompt missing")
    m=json.loads(Path(cfg["benchmark_manifest"]).read_text())
    if m.get("status","").startswith("provenance_manifest_only"):blockers.append("benchmark task materialization pending")
    if cfg.get("real_execution") is not True:blockers.append("real_execution is intentionally disabled")
    if "REPLACE_WITH" in cfg.get("docker_image",""):blockers.append("Docker digest not frozen")
    for e in errors:print("FAIL:",e)
    if errors:raise SystemExit(1)
    if blockers:
        print("AUDIT: FAIL-CLOSED")
        for b in blockers:print("BLOCKED:",b)
        raise SystemExit(2)
    print("AUDIT: PASS")
if __name__=="__main__":main()
