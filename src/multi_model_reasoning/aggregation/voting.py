from collections import Counter

def deterministic_majority(candidates):
    if not candidates: raise ValueError("no candidates")
    counts=Counter(candidates)
    return sorted(counts.items(), key=lambda kv:(-kv[1],candidates.index(kv[0]),kv[0]))[0][0]
