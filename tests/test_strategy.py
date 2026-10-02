from multi_model_reasoning.collaboration.protocols import get_strategy
def test_all_conditions_have_explicit_protocols():
    for c in [f"C{i}" for i in range(7)]:
        s=get_strategy(c);assert s.condition==c and s.calls_per_task>=1
