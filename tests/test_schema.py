import pytest
from multi_model_reasoning.evaluation.schema import validate_result

def base():
    return {
        "experiment_id":"E","run_id":"validation-x","task_id":"T","condition":"C0","seed":1,
        "git_sha":"g","config_hash":"c","benchmark_hash":"b","model_config_hash":"m",
        "prompt_hash":"p","objective_verdict":"x","model_calls":1,"output_tokens":1,
        "latency_seconds":.1,"estimated_cost_usd":0,"validation_only":True,
        "python_version":"py","platform":"test",
        "budget_declared":{
            "max_calls":1,"max_output_tokens":10,"max_wall_seconds":1,"max_estimated_cost_usd":1
        },
        "budget_consumed":{
            "calls":1,"output_tokens":1,"wall_seconds":.1,"estimated_cost_usd":0
        },
        "aggregation_strategy":"identity",
        "execution_trace":[{
            "event":"model_call","model_role":"A","semantic_role":"solver",
            "model_id":"mock","seed":1,"round":1,"order":1,"prompt_version":"solver-v1","input_tokens":1,"output_tokens":1,"latency_seconds":0.1,"estimated_cost_usd":0
        }],
    }

def test_schema_accepts_validation():
    validate_result(base())

def test_schema_rejects_mixed_run_id():
    r=base()
    r["validation_only"]=False
    with pytest.raises(ValueError):
        validate_result(r)

def test_schema_rejects_budget_overflow():
    r=base()
    r["budget_consumed"]["wall_seconds"]=2
    with pytest.raises(ValueError):
        validate_result(r)
