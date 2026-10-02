from multi_model_reasoning.budgeting import Budget
from multi_model_reasoning.collaboration.engine import CollaborationEngine
from multi_model_reasoning.collaboration.protocols import get_strategy
from multi_model_reasoning.models.mock import MockAdapter
from multi_model_reasoning.verification.mock import MockVerifier

def configs():
    return {
        r:{
            "model_id":f"model-{r}",
            "temperature":0.0,
            "top_p":1.0,
            "max_tokens":32,
            "max_input_tokens":512,
            "usd_per_1k_input_tokens":0.0,
            "usd_per_1k_output_tokens":0.0,
            "seed":42,
        } for r in "ABCD"
    }

def role_prompts():
    return {
        "solver":{"path":"prompts/solver-v1.txt","version":"solver-v1","text":"SOLVER"},
        "critic":{"path":"prompts/critic-v1.txt","version":"critic-v1","text":"CRITIC"},
        "verifier":{"path":"prompts/verifier-v1.txt","version":"verifier-v1","text":"VERIFIER"},
        "synthesizer":{"path":"prompts/synthesizer-v1.txt","version":"synthesizer-v1","text":"SYNTHESIZER"},
    }

def test_c1_uses_visible_objective_selector_and_distinct_sample_seeds():
    class Selector:
        def __init__(self):
            self.calls=0
        def select_visible(self,candidates):
            self.calls += 1
            return candidates[0]

    selector=Selector()
    engine=CollaborationEngine({r:MockAdapter(r) for r in "ABCD"},Budget(3,256,30,1))
    _, outputs=engine.run(
        spec=get_strategy("C1"),
        problem="p",
        system_prompt="fallback",
        generation_kwargs={
            "model_configs":configs(),
            "role_prompts":role_prompts(),
            "worst_case_seconds":1,
        },
        verifier=selector,
    )
    assert len(outputs)==3
    assert selector.calls==1
    assert [e["seed"] for e in engine.last_trace if e["event"]=="model_call"]==[42,43,44]
    assert any(e["event"]=="objective_selection" and e["selection_split"]=="visible" for e in engine.last_trace)

def test_c2_uses_three_distinct_model_roles_and_visible_selection():
    class Selector:
        def select_visible(self,candidates):
            return candidates[1]

    engine=CollaborationEngine({r:MockAdapter(r) for r in "ABCD"},Budget(3,256,30,1))
    _, outputs=engine.run(
        spec=get_strategy("C2"),
        problem="p",
        system_prompt="fallback",
        generation_kwargs={
            "model_configs":configs(),
            "role_prompts":role_prompts(),
            "worst_case_seconds":1,
        },
        verifier=Selector(),
    )
    assert len(outputs)==3
    calls=[e for e in engine.last_trace if e["event"]=="model_call"]
    assert [e["model_role"] for e in calls]==["A","B","C"]
    assert all(e["semantic_role"]=="solver" for e in calls)

def test_c5_records_four_roles_and_uses_role_specific_prompt_versions():
    engine=CollaborationEngine({r:MockAdapter(r) for r in "ABCD"},Budget(4,256,30,1))
    final, outputs=engine.run(
        spec=get_strategy("C5"),
        problem="p",
        system_prompt="fallback-must-not-be-used",
        generation_kwargs={
            "model_configs":configs(),
            "role_prompts":role_prompts(),
            "worst_case_seconds":1,
        },
    )
    assert len(outputs)==4
    calls=[e for e in engine.last_trace if e["event"]=="model_call"]
    assert [e["semantic_role"] for e in calls]==["solver","critic","verifier","synthesizer"]
    assert [e["prompt_version"] for e in calls]==[
        "solver-v1","critic-v1","verifier-v1","synthesizer-v1"
    ]
    assert [e["model_role"] for e in calls]==["A","B","C","D"]
