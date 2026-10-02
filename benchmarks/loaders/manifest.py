import json
from pathlib import Path
REQUIRED_TASK_FIELDS={"task_id","task_sha256","test_sha256","prompt","visible_tests","hidden_tests"}
def load_materialized_tasks(path):
    rows=[json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
    if not rows: raise RuntimeError("materialized benchmark is empty")
    for r in rows:
        missing=REQUIRED_TASK_FIELDS-set(r)
        if missing: raise ValueError(f"task {r.get('task_id')} missing {sorted(missing)}")
    return rows
