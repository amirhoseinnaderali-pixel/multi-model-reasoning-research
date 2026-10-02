import pytest

from multi_model_reasoning.budgeting import Budget
from multi_model_reasoning.collaboration.engine import CollaborationEngine
from multi_model_reasoning.collaboration.protocols import get_strategy
from multi_model_reasoning.models.mock import MockAdapter


def model_configs():
    return {
        role: {
            "model_id": f"model-{role}",
            "temperature": 0.0,
            "top_p": 1.0,
            "max_tokens": 32,
            "max_input_tokens": 512,
            "usd_per_1k_input_tokens": 0.0,
            "usd_per_1k_output_tokens": 0.0,
            "seed": 42,
        }
        for role in "ABCD"
    }


def role_prompts():
    return {
        "solver": {
            "path": "prompts/solver-v1.txt",
            "version": "solver-v1",
            "text": "SOLVER",
        },
        "critic": {
            "path": "prompts/critic-v1.txt",
            "version": "critic-v1",
            "text": "CRITIC",
        },
        "verifier": {
            "path": "prompts/verifier-v1.txt",
            "version": "verifier-v1",
            "text": "VERIFIER",
        },
        "synthesizer": {
            "path": "prompts/synthesizer-v1.txt",
            "version": "synthesizer-v1",
            "text": "SYNTHESIZER",
        },
    }


def c6_role_prompts():
    return {
        "solver": {
            "path": "prompts/c6-solver-v1.txt",
            "version": "c6-solver-v1",
            "text": "C6 SOLVER",
        },
        "critic": {
            "path": "prompts/c6-critic-v1.txt",
            "version": "c6-critic-v1",
            "text": "C6 CRITIC",
        },
        "synthesizer": {
            "path": "prompts/c6-synthesizer-v1.txt",
            "version": "c6-synthesizer-v1",
            "text": "C6 SYNTHESIZER",
        },
    }


class VisibleSelector:
    def select_visible(self, candidates):
        return candidates[0]


def run_condition(condition):
    spec = get_strategy(condition)
    engine = CollaborationEngine(
        {role: MockAdapter(role) for role in "ABCD"},
        Budget(spec.calls_per_task, 256, 30, 1),
    )
    generation_kwargs = {
        "model_configs": model_configs(),
        "role_prompts": role_prompts(),
        "role_prompts_by_condition": {"C6": c6_role_prompts()},
        "worst_case_seconds": 1,
    }
    verifier = VisibleSelector() if spec.uses_verifier else None

    final, outputs = engine.run(
        spec=spec,
        problem="regression problem",
        system_prompt="fallback",
        generation_kwargs=generation_kwargs,
        verifier=verifier,
    )
    return engine.last_trace, outputs


@pytest.mark.parametrize(
    ("condition", "expected_roles", "expected_semantic_roles"),
    [
        ("C0", ["A"], ["solver"]),
        ("C1", ["A", "A", "A"], ["solver", "solver", "solver"]),
        ("C2", ["A", "B", "C"], ["solver", "solver", "solver"]),
        ("C3", ["A", "B", "A"], ["solver", "critic", "solver"]),
        ("C4", ["A", "B", "C"], ["solver", "solver", "solver"]),
        ("C5", ["A", "B", "C", "D"], ["solver", "critic", "verifier", "synthesizer"]),
        ("C6", ["A", "B", "C"], ["solver", "critic", "synthesizer"]),
    ],
)
def test_every_condition_reaches_generation_with_correct_argument_order(
    condition, expected_roles, expected_semantic_roles
):
    trace, outputs = run_condition(condition)
    calls = [event for event in trace if event["event"] == "model_call"]

    assert len(outputs) == len(expected_roles)
    assert [call["condition"] for call in calls] == [condition] * len(expected_roles)
    assert [call["model_role"] for call in calls] == expected_roles
    assert [call["semantic_role"] for call in calls] == expected_semantic_roles
    assert all(call["model_role"] in {"A", "B", "C", "D"} for call in calls)
    assert all(call["condition"] not in {"A", "B", "C", "D"} for call in calls)
    assert all("prompt_version" in call for call in calls)


def test_c5_and_c6_regressions_do_not_use_condition_as_model_role():
    for condition, expected_roles in [
        ("C5", {"A", "B", "C", "D"}),
        ("C6", {"A", "B", "C"}),
    ]:
        trace, _ = run_condition(condition)
        calls = [event for event in trace if event["event"] == "model_call"]
        assert all(call["condition"] == condition for call in calls)
        assert all(call["model_role"] in expected_roles for call in calls)
        assert all(call["model_role"] != condition for call in calls)
