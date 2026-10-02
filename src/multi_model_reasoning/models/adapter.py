from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class GenerationResult:
    text: str
    input_tokens: int
    output_tokens: int
    latency_seconds: float
    model_id: str

class ModelAdapter(Protocol):
    def generate(self, *, prompt, system_prompt, model_id, temperature, top_p, max_tokens, seed)->GenerationResult: ...
