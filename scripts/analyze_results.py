#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import sys
sys.path.insert(0,"src")
from multi_model_reasoning.evaluation.statistics import mean,median,bootstrap_ci
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    records=[]
    for f in sorted(Path(a.input).glob("*.json")):
        x=json.loads(f.read_text());records.extend(x if isinstance(x,list) else [x])
    if any(r.get("validation_only") for r in records):raise SystemExit("refusing validation-only records")
    by={}
    for r in records:by.setdefault(r["condition"],[]).append(1 if r["objective_verdict"]=="pass" else 0)
    out={c:{"n":len(v),"mean_accuracy":mean(v),"median_accuracy":median(v),"bootstrap_95_ci":bootstrap_ci(v)} for c,v in by.items()}
    Path(a.output).write_text(json.dumps(out,indent=2)+"\n")
if __name__=="__main__":main()
