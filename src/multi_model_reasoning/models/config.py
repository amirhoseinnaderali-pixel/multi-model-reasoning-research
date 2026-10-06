from dataclasses import dataclass, asdict
import hashlib, json

@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model_id: str
    model_version: str|None
    temperature: float
    top_p: float
    max_tokens: int
    seed: int
    system_prompt_version: str
    def canonical(self): return asdict(self)
    def config_hash(self):
        raw=json.dumps(self.canonical(),sort_keys=True,separators=(",",":"))
        return hashlib.sha256(raw.encode()).hexdigest()
