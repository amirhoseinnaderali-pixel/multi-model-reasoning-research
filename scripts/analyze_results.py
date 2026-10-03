#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from pathlib import Path
import sys

sys.path.insert(0,"src")
from multi_model_reasoning.evaluation.statistics import mean, median, bootstrap_ci, holm_bonferroni, paired_bootstrap_ci, paired_differences, paired_sign_flip_pvalue

EVALUABLE={"pass","wrong_answer","timeout","malformed_output"}
FAILURE_CLASSES={"model_failure","infrastructure_failure"}

def load_records(path):
    records=[]
    for f in sorted(Path(path).glob("*.json")):
        value=json.loads(f.read_text())
        records.extend(value if isinstance(value,list) else [value])
    if any(r.get("validation_only") for r in records):
        raise SystemExit("refusing validation-only records")
    return records

def summarize(records):
    grouped=defaultdict(list)
    for r in records:
        grouped[(r["condition"],r.get("budget_id","UNSPECIFIED"))].append(r)
    out={}
    for (condition,budget), rows in sorted(grouped.items()):
        verdicts=[r["objective_verdict"] for r in rows]
        passes=sum(v=="pass" for v in verdicts)
        evaluable=sum(v in EVALUABLE for v in verdicts)
        out[f"{condition}:{budget}"]={
            "n_runs":len(rows),
            "passes":passes,
            "evaluable_runs":evaluable,
            "accuracy_on_evaluable_runs":passes/evaluable if evaluable else None,
            "overall_run_pass_rate":passes/len(rows) if rows else None,
            "failure_counts":{v:verdicts.count(v) for v in sorted(set(verdicts))},
            "mean_model_calls":mean([r["model_calls"] for r in rows]),
            "median_model_calls":median([r["model_calls"] for r in rows]),
            "mean_output_tokens":mean([r["output_tokens"] for r in rows]),
            "mean_latency_seconds":mean([r["latency_seconds"] for r in rows]),
            "mean_estimated_cost_usd":mean([r["estimated_cost_usd"] for r in rows]),
            "correctness_per_call":passes/sum(r["model_calls"] for r in rows) if sum(r["model_calls"] for r in rows) else None,
            "correctness_per_token":passes/sum(r["output_tokens"] for r in rows) if sum(r["output_tokens"] for r in rows) else None,
        }
    pvalues={condition: value.get("paired_sign_flip_p") for condition, value in out.items() if value.get("paired_sign_flip_p") is not None}
    adjusted=holm_bonferroni(pvalues)
    for condition in out:
        out[condition]["holm_adjusted_p"]=adjusted.get(condition)
    return out

def paired_summary(records):
    out={}
    for condition in sorted({r["condition"] for r in records if r["condition"]!="C0"}):
        diffs=paired_differences(records,condition,baseline="C0")
        out[condition]={
            "paired_n":len(diffs),
            "mean_accuracy_difference_vs_C0":mean(diffs),
            "bootstrap_95_ci_difference":paired_bootstrap_ci(diffs) if diffs else (None,None),
        }
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    records=load_records(a.input)
    if not records:
        raise SystemExit("no scientific result records found")
    out={
        "analysis_status":"computed_from_real_records",
        "n_records":len(records),
        "by_condition_and_budget":summarize(records),
        "paired_vs_C0":paired_summary(records),
        "note":"Infrastructure/model failures are reported separately and are not silently counted as wrong answers.",
    }
    Path(a.output).write_text(json.dumps(out,indent=2)+"\n")

if __name__=="__main__":
    main()
