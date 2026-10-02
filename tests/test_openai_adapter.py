import pytest
from multi_model_reasoning.models.openai_adapter import OpenAIAdapter
def test_real_adapter_fails_closed_without_credentials(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY",raising=False)
    with pytest.raises(RuntimeError):OpenAIAdapter()
