REQUIRED_RESULT_FIELDS = {
    "experiment_id","run_id","run_scope","task_id","condition","strategy","seed",
    "git_sha","config_hash","benchmark_hash","task_hash","model_config_hash","prompt_hash",
    "docker_digest","timestamp_utc","objective_verdict","failure_classification","failure_message",
    "model_calls","output_tokens","latency_seconds","estimated_cost_usd","validation_only",
    "python_version","platform","package_versions","budget_declared","budget_consumed",
    "aggregation_strategy","execution_trace",
}


def validate_result(record):
    missing = REQUIRED_RESULT_FIELDS - set(record)
    if missing:
        raise ValueError(f"missing result fields: {sorted(missing)}")

    if record["run_scope"] not in {"validation_only", "smoke_test", "scientific_results"}:
        raise ValueError(f"invalid run_scope: {record['run_scope']}")
    if record["run_scope"] == "validation_only" and not record["validation_only"]:
        raise ValueError("validation_only scope must set validation_only=true")
    if record["run_scope"] != "validation_only" and record["validation_only"]:
        raise ValueError("non-validation scopes must set validation_only=false")
    if record["run_scope"] == "scientific_results" and str(record["run_id"]).startswith("validation-"):
        raise ValueError("scientific runs cannot use validation-* IDs")
    if record["docker_digest"] != "NOT_EXECUTED" and "@sha256:" not in str(record["docker_digest"]):
        raise ValueError("docker_digest must be immutable or NOT_EXECUTED")
    if not isinstance(record["package_versions"], dict):
        raise ValueError("package_versions must be a dictionary")

    declared = record["budget_declared"]
    consumed = record["budget_consumed"]
    for key in ("max_calls","max_output_tokens","max_wall_seconds","max_estimated_cost_usd"):
        if key not in declared:
            raise ValueError(f"budget declaration missing {key}")
    if consumed.get("calls", 0) > declared["max_calls"]:
        raise ValueError("call budget exceeded")
    if consumed.get("output_tokens", 0) > declared["max_output_tokens"]:
        raise ValueError("token budget exceeded")
    if consumed.get("wall_seconds", 0) > declared["max_wall_seconds"]:
        raise ValueError("wall-clock budget exceeded")
    if consumed.get("estimated_cost_usd", 0) > declared["max_estimated_cost_usd"]:
        raise ValueError("cost budget exceeded")

    trace = record["execution_trace"]
    if not isinstance(trace, list):
        raise ValueError("execution_trace must be a list")

    required_call_fields = {
        "condition","model_role","semantic_role","model_id","seed","round","order",
        "prompt_version","input_tokens","output_tokens","latency_seconds","estimated_cost_usd",
    }
    required_failure_fields = {
        "condition","model_role","semantic_role","model_id","seed","round","order",
        "prompt_version","failure_classification","failure_message",
        "reserved_output_tokens","reserved_wall_seconds","reserved_cost_usd",
    }
    for event in trace:
        if event.get("event") == "model_call":
            missing_trace = required_call_fields - set(event)
            if missing_trace:
                raise ValueError(f"model trace missing {sorted(missing_trace)}")
        elif event.get("event") == "model_call_failure":
            missing_trace = required_failure_fields - set(event)
            if missing_trace:
                raise ValueError(f"failed model trace missing {sorted(missing_trace)}")
