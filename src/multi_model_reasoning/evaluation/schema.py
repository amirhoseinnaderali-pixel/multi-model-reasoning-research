REQUIRED_RESULT_FIELDS={
    "experiment_id","run_id","task_id","condition","seed",
    "git_sha","config_hash","benchmark_hash","model_config_hash","prompt_hash",
    "objective_verdict","model_calls","output_tokens","latency_seconds",
    "estimated_cost_usd","validation_only","python_version","platform",
    "budget_declared","budget_consumed","aggregation_strategy","execution_trace",
}

def validate_result(record):
    missing=REQUIRED_RESULT_FIELDS-set(record)
    if missing:
        raise ValueError(f"missing result fields: {sorted(missing)}")
    if record["validation_only"] and not str(record["run_id"]).startswith("validation-"):
        raise ValueError("validation_only records must use validation-* IDs")
    if not record["validation_only"] and str(record["run_id"]).startswith("validation-"):
        raise ValueError("scientific runs cannot use validation-* IDs")

    d=record["budget_declared"]
    c=record["budget_consumed"]
    for k in ("max_calls","max_output_tokens","max_wall_seconds","max_estimated_cost_usd"):
        if k not in d:
            raise ValueError(f"budget declaration missing {k}")

    if c.get("calls",0)>d["max_calls"]:
        raise ValueError("call budget exceeded")
    if c.get("output_tokens",0)>d["max_output_tokens"]:
        raise ValueError("token budget exceeded")
    if c.get("wall_seconds",0)>d["max_wall_seconds"]:
        raise ValueError("wall-clock budget exceeded")
    if c.get("estimated_cost_usd",0)>d["max_estimated_cost_usd"]:
        raise ValueError("cost budget exceeded")

    trace=record["execution_trace"]
    if not isinstance(trace,list):
        raise ValueError("execution_trace must be a list")
    for event in trace:
        if event.get("event")=="model_call":
            for field in ("model_role","semantic_role","model_id","seed","prompt_version"):
                if field not in event:
                    raise ValueError(f"model trace missing {field}")
