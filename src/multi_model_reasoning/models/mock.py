from .adapter import GenerationResult


class MockAdapter:
    """Deterministic validation-only adapter; never scientific evidence."""

    def __init__(self, label="mock"):
        self.label = label

    def generate(
        self,
        *,
        prompt,
        system_prompt,
        model_id,
        temperature,
        top_p,
        max_tokens,
        seed,
        api_endpoint=None,
        reasoning_effort=None,
        service_tier=None,
    ):
        text = (
            "# validation_only\n"
            f"# seed={seed}\n"
            f"# model={model_id}\n"
            "def solution(*args, **kwargs):\n"
            "    return None\n"
        )
        return GenerationResult(
            text,
            len(prompt.split()),
            min(24, max_tokens),
            0.001,
            model_id,
        )
