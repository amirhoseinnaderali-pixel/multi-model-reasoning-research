import pytest
from multi_model_reasoning.budgeting import Budget,BudgetExceeded
def test_budget_reserves_before_generation():
    b=Budget(1,10,5,1);b.reserve_call(requested_output_tokens=10,worst_case_seconds=5)
    with pytest.raises(BudgetExceeded):b.reserve_call(requested_output_tokens=1,worst_case_seconds=1)
def test_actual_overflow_fails():
    b=Budget(1,10,5,1);b.reserve_call(requested_output_tokens=10,worst_case_seconds=5)
    with pytest.raises(BudgetExceeded):b.settle_call(actual_output_tokens=11,actual_wall_seconds=6,reserved_output_tokens=10,reserved_wall_seconds=5)
