#!/usr/bin/env python3
import argparse,json,os,shutil
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True)
    a=ap.parse_args()
    cfg=json.loads(Path(a.config).read_text())
    errors=[]
    manifest=Path(cfg["benchmark_manifest"])
    tasks=Path(cfg["materialized_tasks"])
    models=Path(cfg["models"])

    if not manifest.exists(): errors.append("benchmark manifest missing")
    if not tasks.exists(): errors.append("materialized task file missing")
    if not models.exists(): errors.append("model config missing")

    role_prompts=cfg.get("role_prompts",{})
    required_prompts={"solver","critic","verifier","synthesizer"}
    if required_prompts-set(role_prompts):
        errors.append("C5 role prompt mapping is incomplete")
    for role in sorted(required_prompts & set(role_prompts)):
        path=Path(role_prompts[role])
        if not path.exists():
            errors.append(f"missing role prompt artifact: {role}")
        elif not path.read_text().splitlines() or not path.read_text().splitlines()[0].startswith("VERSION:"):
            errors.append(f"role prompt lacks explicit VERSION header: {role}")

    if manifest.exists() and json.loads(manifest.read_text()).get("status","").startswith("provenance_manifest_only"):
        errors.append("benchmark task materialization pending")

    if tasks.exists():
        rows=[json.loads(x) for x in tasks.read_text().splitlines() if x.strip()]
        if len(rows)!=100:
            errors.append("EXP-001 requires exactly 100 frozen tasks")
        for r in rows:
            if not all(k in r for k in ("task_id","task_sha256","test_sha256","prompt","visible_tests","hidden_tests")):
                errors.append("task schema incomplete")
                break

    md=json.loads(models.read_text()) if models.exists() else {}
    for role in "ABCD":
        x=md.get("models",{}).get(role)
        if not x:
            errors.append(f"missing model role {role}")
            continue
        if str(x.get("model_id","")).startswith("REPLACE_WITH"):
            errors.append(f"model role {role} is not frozen")
        if x.get("model_version") in (None,"REQUIRED"):
            errors.append(f"model version {role} is not frozen")
        if x.get("cost_status")=="MUST_BE_FROZEN_BEFORE_REAL_RUN":
            errors.append(f"pricing {role} is not frozen")
        for field in ("usd_per_1k_input_tokens","usd_per_1k_output_tokens"):
            value=x.get(field)
            if not isinstance(value,(int,float)) or value<0:
                errors.append(f"invalid {field} for model role {role}")
        if x.get("max_input_tokens",0)<=0 or x.get("max_tokens",0)<=0:
            errors.append(f"token limits must be positive for model role {role}")

    if "REPLACE_WITH" in cfg.get("docker_image",""):
        errors.append("Docker digest not frozen")
    if shutil.which("docker") is None:
        errors.append("Docker CLI unavailable")
    if not os.getenv("OPENAI_API_KEY"):
        errors.append("OPENAI_API_KEY unavailable")
    if cfg.get("real_execution") is not True:
        errors.append("experiment config is intentionally non-executable")

    print("READY" if not errors else "NOT READY")
    for item in errors:
        print("BLOCKED:",item)
    raise SystemExit(0 if not errors else 2)

if __name__=="__main__":
    main()
