from multi_model_reasoning.budgeting import Budget

def test_actual_cost_is_recorded_without_exceeding_reserved_budget():
    b=Budget(1,100,10,1.0)
    b.reserve_call(requested_output_tokens=50, worst_case_seconds=5, estimated_cost_usd=0.5)
    b.settle_call(
        actual_output_tokens=20,
        actual_cost_usd=0.2,
        actual_wall_seconds=1,
        reserved_output_tokens=50,
        reserved_wall_seconds=5,
        reserved_cost_usd=0.5,
    )
    assert b.output_tokens==20
    assert b.estimated_cost_usd==0.2
    assert b.reserved_output_tokens==0
    assert b.reserved_cost_usd==0
