import math
import random
from collections import defaultdict

def mean(xs):
    return sum(xs)/len(xs) if xs else math.nan

def median(xs):
    if not xs:
        return math.nan
    ys=sorted(xs); n=len(ys); m=n//2
    return ys[m] if n%2 else (ys[m-1]+ys[m])/2

def _cluster_means(values, clusters):
    values=list(values); clusters=list(clusters)
    if len(values)!=len(clusters):
        raise ValueError("values and clusters must have equal length")
    grouped=defaultdict(list)
    for value, cluster in zip(values, clusters):
        grouped[cluster].append(value)
    return [mean(grouped[key]) for key in sorted(grouped)]

def bootstrap_ci(xs, *, seed=0, n_boot=10000, alpha=0.05, clusters=None):
    if clusters is not None:
        xs=_cluster_means(xs, clusters)
    if not xs:
        return (math.nan, math.nan)
    rng=random.Random(seed); n=len(xs); vals=[]
    for _ in range(n_boot):
        vals.append(mean([xs[rng.randrange(n)] for _ in range(n)]))
    vals.sort()
    return vals[int(alpha/2*len(vals))], vals[int((1-alpha/2)*len(vals))-1]

def paired_bootstrap_ci(differences, *, seed=0, n_boot=10000, alpha=0.05):
    return bootstrap_ci(differences, seed=seed, n_boot=n_boot, alpha=alpha)

def paired_sign_flip_pvalue(differences, *, seed=2468, n_boot=10000):
    if not differences:
        return math.nan
    observed=abs(mean(differences))
    if all(value == 0 for value in differences):
        return 1.0
    rng=random.Random(seed)
    extreme=0
    n=len(differences)
    for _ in range(n_boot):
        signed=[value if rng.getrandbits(1) else -value for value in differences]
        if abs(mean(signed)) >= observed:
            extreme += 1
    return (extreme+1)/(n_boot+1)

def holm_bonferroni(pvalues):
    ordered=sorted(pvalues.items(), key=lambda item: item[1])
    adjusted={}
    running=0.0
    m=len(ordered)
    for i,(key,pvalue) in enumerate(ordered):
        running=max(running, min(1.0, pvalue*(m-i)))
        adjusted[key]=running
    return adjusted

def paired_differences(records, condition, baseline="C0"):
    by_task=defaultdict(lambda: {"candidate": [], "baseline": []})
    for r in records:
        side="baseline" if r["condition"]==baseline else "candidate" if r["condition"]==condition else None
        if side is not None:
            outcome=1 if r["objective_verdict"]=="pass" else 0
            by_task[r["task_id"]][side].append(outcome)
    out=[]
    for task_id in sorted(by_task):
        pair=by_task[task_id]
        if pair["candidate"] and pair["baseline"]:
            out.append(mean(pair["candidate"])-mean(pair["baseline"]))
    return out
