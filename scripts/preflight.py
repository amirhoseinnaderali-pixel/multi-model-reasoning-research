#!/usr/bin/env python3
import argparse,json,os,shutil
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--config",required=True); a=ap.parse_args(); cfg=json.loads(Path(a.config).read_text()); e=[]
    manifest=Path(cfg["benchmark_manifest"]); tasks=Path(cfg["materialized_tasks"]); models=Path(cfg["models"])
    if not manifest.exists(): e.append("benchmark manifest missing")
    if not tasks.exists(): e.append("materialized task file missing")
    if not models.exists(): e.append("model config missing")
    if manifest.exists() and json.loads(manifest.read_text()).get("status","").startswith("provenance_manifest_only"): e.append("benchmark task materialization pending")
    if tasks.exists():
        rows=[json.loads(x) for x in tasks.read_text().splitlines() if x.strip()]
        if len(rows)!=100:e.append("EXP-001 requires exactly 100 frozen tasks")
        for r in rows:
            if not all(k in r for k in ("task_id","task_sha256","test_sha256","prompt","visible_tests","hidden_tests")):e.append("task schema incomplete");break
    md=json.loads(models.read_text()) if models.exists() else {}
    for role in "ABCD":
        x=md.get("models",{}).get(role)
        if not x:e.append(f"missing model role {role}")
        elif str(x["model_id"]).startswith("REPLACE_WITH"):e.append(f"model role {role} is not frozen")
        elif x.get("model_version") in (None,"REQUIRED"):e.append(f"model version {role} is not frozen")
        elif x.get("cost_status")=="MUST_BE_FROZEN_BEFORE_REAL_RUN":e.append(f"pricing {role} is not frozen")
    if "REPLACE_WITH" in cfg.get("docker_image",""):e.append("Docker digest not frozen")
    if shutil.which("docker") is None:e.append("Docker CLI unavailable")
    if not os.getenv("OPENAI_API_KEY"):e.append("OPENAI_API_KEY unavailable")
    if cfg.get("real_execution") is not True:e.append("experiment config is intentionally non-executable")
    print("READY" if not e else "NOT READY")
    for x in e: print("BLOCKED:",x)
    raise SystemExit(0 if not e else 2)
if __name__=="__main__":main()
