from dataclasses import dataclass,asdict
from datetime import datetime,timezone
import hashlib,json,platform,subprocess,sys
@dataclass(frozen=True)
class RunManifest:
    experiment_id:str; run_id:str; git_sha:str; config_hash:str; benchmark_hash:str; model_config_hash:str; strategy:str; seed:int; budget:dict; timestamp_utc:str; python_version:str; platform:str; package_versions:dict
    @classmethod
    def create(cls,**kwargs): return cls(timestamp_utc=datetime.now(timezone.utc).isoformat(),python_version=sys.version,platform=platform.platform(),**kwargs)
def hash_json(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def git_sha():
    try:return subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    except Exception:return "UNKNOWN"
