from multi_model_reasoning.collaboration.protocols import get_strategy

def test_all_conditions_have_explicit_protocols():
    for c in [f"C{i}" for i in range(7)]:
        s=get_strategy(c)
        assert s.condition==c
        assert s.calls_per_task>=1

def test_c1_c2_use_objective_visible_selection_not_text_majority():
    assert get_strategy("C1").aggregation=="visible_objective_selection"
    assert get_strategy("C2").aggregation=="visible_objective_selection"
    assert get_strategy("C1").uses_verifier
    assert get_strategy("C2").uses_verifier

def test_c5_has_explicit_semantic_roles():
    s=get_strategy("C5")
    assert s.semantic_roles==("solver","critic","verifier","synthesizer")
    assert s.aggregation=="role_specialized_final"
    assert not s.uses_verifier
