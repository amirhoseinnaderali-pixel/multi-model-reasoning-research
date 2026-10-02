from .adapter import GenerationResult

class MockAdapter:
    """Deterministic validation-only adapter; never scientific evidence."""
    def __init__(self,label="mock"): self.label=label
    def generate(self, *, prompt, system_prompt, model_id, temperature, top_p, max_tokens, seed):
        text=f"# validation_only\n# seed={seed}\n# model={model_id}\ndef solution(*args, **kwargs):\n    return None\n"
        return GenerationResult(text, len(prompt.split()), min(24,max_tokens), 0.001, model_id)
