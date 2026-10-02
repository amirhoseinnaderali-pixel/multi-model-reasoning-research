import json
from pathlib import Path
def load_json(path): return json.loads(Path(path).read_text(encoding="utf-8"))
