import math
import random

def mean(xs):
    return sum(xs)/len(xs) if xs else math.nan

def median(xs):
    if not xs:
        return math.nan
    ys=sorted(xs); n=len(ys); m=n//2
    return ys[m] if n%2 else (ys[m-1]+ys[m])/2

def bootstrap_ci(xs, *, seed=0, n_boot=5000, alpha=0.05):
    if not xs:
        return (math.nan, math.nan)
    rng=random.Random(seed); n=len(xs); vals=[]
    for _ in range(n_boot):
        vals.append(mean([xs[rng.randrange(n)] for _ in range(n)]))
    vals.sort()
    return vals[int(alpha/2*len(vals))], vals[int((1-alpha/2)*len(vals))-1]

def paired_bootstrap_ci(differences, *, seed=0, n_boot=5000, alpha=0.05):
    return bootstrap_ci(differences, seed=seed, n_boot=n_boot, alpha=alpha)

def paired_differences(records, condition, baseline="C0"):
    baseline_by_key={(r["task_id"],r["seed"],r.get("budget_id")):
                     (1 if r["objective_verdict"]=="pass" else 0)
                     for r in records if r["condition"]==baseline}
    out=[]
    for r in records:
        if r["condition"]!=condition:
            continue
        key=(r["task_id"],r["seed"],r.get("budget_id"))
        if key in baseline_by_key:
            outcome=1 if r["objective_verdict"]=="pass" else 0
            out.append(outcome-baseline_by_key[key])
    return out
