from multi_model_reasoning.budgeting import Budget
from multi_model_reasoning.collaboration.engine import CollaborationEngine
from multi_model_reasoning.collaboration.protocols import get_strategy
from multi_model_reasoning.models.mock import MockAdapter


class FailingAdapter:
    def generate(self, **kwargs):
        raise RuntimeError("authentication failed: test credential")


def test_failed_model_call_is_settled_and_classified():
    engine = CollaborationEngine({"A": FailingAdapter()}, Budget(1, 64, 10, 1.0))
    try:
        engine.run(
            spec=get_strategy("C0"),
            problem="p",
            system_prompt="s",
            generation_kwargs={
                "model_configs": {
                    "A": {
                        "model_id":"model-A","temperature":0.0,"top_p":1.0,
                        "max_tokens":32,"max_input_tokens":64,
                        "usd_per_1k_input_tokens":0.01,"usd_per_1k_output_tokens":0.02,"seed":42,
                    }
                },
                "role_prompts":{"solver":{"path":"p","version":"v1","text":"S"}},
                "worst_case_seconds":1,
            },
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected failure")
    assert engine.budget.calls == 1
    assert engine.budget.reserved_output_tokens == 0
    assert engine.budget.reserved_cost_usd == 0
    failure = [e for e in engine.last_trace if e["event"] == "model_call_failure"][0]
    assert failure["failure_classification"] == "credential_failure"
