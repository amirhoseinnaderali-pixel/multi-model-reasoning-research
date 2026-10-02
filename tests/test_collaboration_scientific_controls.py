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

class RecordingAdapter:
    def __init__(self, role):
        self.role=role
        self.calls=[]

    def generate(self, *, prompt, system_prompt, model_id, temperature, top_p, max_tokens, seed):
        from multi_model_reasoning.models.adapter import GenerationResult
        self.calls.append({"prompt":prompt,"system_prompt":system_prompt})
        return GenerationResult(
            text=f"{self.role}-output",
            input_tokens=len(prompt.split()),
            output_tokens=1,
            latency_seconds=0.001,
            model_id=model_id,
        )

def test_c5_information_visibility_is_explicit():
    adapters={r:RecordingAdapter(r) for r in "ABCD"}
    engine=CollaborationEngine(adapters,Budget(4,256,30,1))
    engine.run(
        spec=get_strategy("C5"),
        problem="ORIGINAL PROBLEM",
        system_prompt="fallback-must-not-be-used",
        generation_kwargs={
            "model_configs":configs(),
            "role_prompts":role_prompts(),
            "worst_case_seconds":1,
        },
    )
    assert "ORIGINAL PROBLEM" in adapters["A"].calls[0]["prompt"]
    assert "A-output" in adapters["B"].calls[0]["prompt"]
    assert "A-output" in adapters["C"].calls[0]["prompt"]
    assert "B-output" in adapters["C"].calls[0]["prompt"]
    assert "A-output" in adapters["D"].calls[0]["prompt"]
    assert "B-output" in adapters["D"].calls[0]["prompt"]
    assert "C-output" in adapters["D"].calls[0]["prompt"]
    assert "HIDDEN" not in adapters["C"].calls[0]["prompt"]
    assert [c["system_prompt"] for c in adapters["A"].calls] == ["SOLVER"]
    assert [c["system_prompt"] for c in adapters["B"].calls] == ["CRITIC"]
    assert [c["system_prompt"] for c in adapters["C"].calls] == ["VERIFIER"]
    assert [c["system_prompt"] for c in adapters["D"].calls] == ["SYNTHESIZER"]


def c6_role_prompts():
    return {
        "solver":{"path":"prompts/c6-solver-v1.txt","version":"c6-solver-v1","text":"C6 SOLVER"},
        "critic":{"path":"prompts/c6-critic-v1.txt","version":"c6-critic-v1","text":"C6 CRITIC"},
        "synthesizer":{"path":"prompts/c6-synthesizer-v1.txt","version":"c6-synthesizer-v1","text":"C6 SYNTHESIZER"},
    }

def test_c6_has_collaborative_semantic_roles_and_differs_from_c2():
    c6=get_strategy("C6")
    c2=get_strategy("C2")
    assert c6.semantic_roles==("solver","critic","synthesizer")
    assert c6.rounds==3
    assert c6.uses_verifier
    assert c6.aggregation=="sequential_refinement_visible_selection"
    assert c6.semantic_roles!=c2.semantic_roles
    assert c6.description!=c2.description

def test_c6_model_b_receives_a_and_c_receives_a_and_b():
    adapters={r:RecordingAdapter(r) for r in "ABCD"}
    engine=CollaborationEngine(adapters,Budget(3,256,30,1))
    engine.run(
        spec=get_strategy("C6"),
        problem="ORIGINAL",
        system_prompt="fallback",
        generation_kwargs={
            "model_configs":configs(),
            "role_prompts":role_prompts(),
            "role_prompts_by_condition":{"C6":c6_role_prompts()},
            "worst_case_seconds":1,
        },
        verifier=type("Selector",(),{"select_visible":lambda self,candidates:candidates[-1]})(),
    )
    assert "ORIGINAL" in adapters["A"].calls[0]["prompt"]
    assert "A-output" in adapters["B"].calls[0]["prompt"]
    assert "ORIGINAL" in adapters["B"].calls[0]["prompt"]
    assert "A-output" in adapters["C"].calls[0]["prompt"]
    assert "B-output" in adapters["C"].calls[0]["prompt"]

def test_c6_hidden_test_changes_do_not_change_collaboration_or_selection():
    class HiddenAwareSelector:
        def __init__(self, hidden):
            self.hidden=hidden
            self.visible_calls=[]
        def select_visible(self,candidates):
            self.visible_calls.append(tuple(candidates))
            return candidates[-1]

    def run(hidden):
        adapters={r:RecordingAdapter(r) for r in "ABCD"}
        selector=HiddenAwareSelector(hidden)
        engine=CollaborationEngine(adapters,Budget(3,256,30,1))
        selected,_=engine.run(
            spec=get_strategy("C6"),
            problem="ORIGINAL",
            system_prompt="fallback",
            generation_kwargs={
                "model_configs":configs(),
                "role_prompts":role_prompts(),
                "role_prompts_by_condition":{"C6":c6_role_prompts()},
                "worst_case_seconds":1,
            },
            verifier=selector,
        )
        prompts={r:adapters[r].calls[0]["prompt"] for r in ("A","B","C")}
        return prompts, selected, selector.visible_calls

    p1,s1,v1=run("HIDDEN_SET_1")
    p2,s2,v2=run("HIDDEN_SET_2")
    assert p1==p2
    assert s1==s2
    assert v1==v2

def test_c6_trace_contains_role_prompt_round_order_tokens_latency_and_cost():
    engine=CollaborationEngine({r:MockAdapter(r) for r in "ABCD"},Budget(3,256,30,1))
    engine.run(
        spec=get_strategy("C6"),
        problem="p",
        system_prompt="fallback",
        generation_kwargs={
            "model_configs":configs(),
            "role_prompts":role_prompts(),
            "role_prompts_by_condition":{"C6":c6_role_prompts()},
            "worst_case_seconds":1,
        },
        verifier=type("Selector",(),{"select_visible":lambda self,candidates:candidates[-1]})(),
    )
    calls=[e for e in engine.last_trace if e["event"]=="model_call"]
    assert [(e["model_role"],e["semantic_role"],e["round"],e["order"]) for e in calls]==[
        ("A","solver",1,1),("B","critic",2,2),("C","synthesizer",3,3)
    ]
    assert all(e["condition"]=="C6" for e in calls)
    assert all(e["prompt_version"].startswith("c6-") for e in calls)
    assert all("input_tokens" in e and "output_tokens" in e and "latency_seconds" in e and "estimated_cost_usd" in e for e in calls)
    assert engine.last_trace[-1]["selection_split"]=="visible"

def test_c6_is_deterministic_for_identical_inputs():
    def run_once():
        engine=CollaborationEngine({r:MockAdapter(r) for r in "ABCD"},Budget(3,256,30,1))
        final,outputs=engine.run(
            spec=get_strategy("C6"),
            problem="same problem",
            system_prompt="fallback",
            generation_kwargs={
                "model_configs":configs(),
                "role_prompts":role_prompts(),
                "role_prompts_by_condition":{"C6":c6_role_prompts()},
                "worst_case_seconds":1,
            },
            verifier=type("Selector",(),{"select_visible":lambda self,candidates:candidates[-1]})(),
        )
        return final,[x.text for x in outputs],[(e["semantic_role"],e["prompt_version"]) for e in engine.last_trace if e["event"]=="model_call"]
    assert run_once()==run_once()

def test_c6_propagates_infrastructure_failure_without_marking_wrong_answer():
    class BrokenSelector:
        def select_visible(self,candidates):
            raise RuntimeError("docker unavailable")
    engine=CollaborationEngine({r:MockAdapter(r) for r in "ABCD"},Budget(3,256,30,1))
    import pytest
    with pytest.raises(RuntimeError,match="docker unavailable"):
        engine.run(
            spec=get_strategy("C6"),
            problem="p",
            system_prompt="fallback",
            generation_kwargs={
                "model_configs":configs(),
                "role_prompts":role_prompts(),
                "role_prompts_by_condition":{"C6":c6_role_prompts()},
                "worst_case_seconds":1,
            },
            verifier=BrokenSelector(),
        )


def test_c6_candidate_verifier_uses_visible_tests_only_and_ignores_hidden_data():
    from multi_model_reasoning.verification.docker_verifier import CandidateVerifier
    from multi_model_reasoning.verification.result import VerificationResult, Verdict

    class RecordingExecutionVerifier:
        def __init__(self):
            self.test_sources=[]
        def verify(self, code, test_source, timeout_seconds):
            self.test_sources.append(test_source)
            passed=1 if code=="A" else 0
            return VerificationResult(Verdict.PASS, passed, 1, 0.1, "")

    def select(hidden_tests):
        cv=CandidateVerifier.__new__(CandidateVerifier)
        cv.verifier=RecordingExecutionVerifier()
        cv.visible_tests="VISIBLE"
        cv.hidden_tests=hidden_tests
        cv.timeout_seconds=1.0
        selected=cv.select_visible(["A","B"])
        return selected, cv.verifier.test_sources

    selected1, sources1=select("HIDDEN-ONE")
    selected2, sources2=select("HIDDEN-TWO")
    assert selected1==selected2=="A"
    assert sources1==sources2==["VISIBLE","VISIBLE"]
    
def test_c6_visible_selection_is_deterministic_on_ties():
    from multi_model_reasoning.verification.docker_verifier import CandidateVerifier
    from multi_model_reasoning.verification.result import VerificationResult, Verdict

    class EqualExecutionVerifier:
        def verify(self, code, test_source, timeout_seconds):
            return VerificationResult(Verdict.PASS, 1, 1, 0.1, "")

    cv=CandidateVerifier.__new__(CandidateVerifier)
    cv.verifier=EqualExecutionVerifier()
    cv.visible_tests="VISIBLE"
    cv.hidden_tests="HIDDEN"
    cv.timeout_seconds=1.0
    assert cv.select_visible(["B","A"])=="B"
    assert cv.select_visible(["B","A"])=="B"

def test_c6_infrastructure_failure_stays_distinct():
    from multi_model_reasoning.verification.docker_verifier import CandidateVerifier
    from multi_model_reasoning.verification.result import VerificationResult, Verdict

    class BrokenExecutionVerifier:
        def verify(self, code, test_source, timeout_seconds):
            return VerificationResult(Verdict.INFRA_FAILURE, 0, 0, 0.1, "docker unavailable")

    cv=CandidateVerifier.__new__(CandidateVerifier)
    cv.verifier=BrokenExecutionVerifier()
    cv.visible_tests="VISIBLE"
    cv.hidden_tests="HIDDEN"
    cv.timeout_seconds=1.0

    import pytest
    with pytest.raises(RuntimeError,match="docker unavailable"):
        cv.select_visible(["A","C"])


def test_c2_candidates_are_independent_and_receive_no_prior_outputs():
    adapters = {r: RecordingAdapter(r) for r in "ABCD"}
    engine = CollaborationEngine(adapters, Budget(3, 256, 30, 1))
    engine.run(
        spec=get_strategy("C2"),
        problem="ORIGINAL",
        system_prompt="fallback",
        generation_kwargs={
            "model_configs": configs(),
            "role_prompts": role_prompts(),
            "worst_case_seconds": 1,
        },
        verifier=type("Selector", (), {"select_visible": lambda self, candidates: candidates[0]})(),
    )
    prompts = [adapters[r].calls[0]["prompt"] for r in ("A", "B", "C")]
    assert prompts == ["ORIGINAL", "ORIGINAL", "ORIGINAL"]
    assert all("A-output" not in p and "B-output" not in p and "C-output" not in p for p in prompts)
