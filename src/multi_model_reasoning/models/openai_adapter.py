import os
import time


class OpenAIAdapter:
    def __init__(self, *, api_endpoint="https://api.openai.com/v1"):
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required")
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError("install optional dependency: pip install -e '.[real]'") from e
        self.api_endpoint = api_endpoint
        self.client = OpenAI(base_url=api_endpoint)

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
        if api_endpoint and api_endpoint != self.api_endpoint:
            raise RuntimeError(f"API endpoint mismatch: frozen={api_endpoint!r} configured={self.api_endpoint!r}")
        start = time.monotonic()
        kwargs = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "top_p": top_p,
            "max_completion_tokens": max_tokens,
            "seed": seed,
        }
        if reasoning_effort is not None:
            kwargs["reasoning_effort"] = reasoning_effort
        if service_tier is not None:
            kwargs["service_tier"] = service_tier
        r = self.client.chat.completions.create(**kwargs)
        usage = r.usage
        return type(
            "GenerationResult",
            (),
            {
                "text": r.choices[0].message.content or "",
                "input_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
                "output_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
                "latency_seconds": time.monotonic() - start,
                "model_id": getattr(r, "model", model_id),
                "system_fingerprint": getattr(r, "system_fingerprint", None),
                "service_tier": getattr(r, "service_tier", service_tier),
            },
        )()
