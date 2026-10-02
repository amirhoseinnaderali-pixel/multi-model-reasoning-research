REQUIRED_RESULT_FIELDS = {
    "experiment_id",
    "run_id",
    "run_scope",
    "task_id",
    "condition",
    "strategy",
    "seed",
    "git_sha",
    "config_hash",
    "benchmark_hash",
    "model_config_hash",
    "prompt_hash",
    "docker_digest",
    "timestamp_utc",
    "objective_verdict",
    "model_calls",
    "output_tokens",
    "latency_seconds",
    "estimated_cost_usd",
    "validation_only",
    "python_version",
    "platform",
    "package_versions",
    "budget_declared",
    "budget_consumed",
    "aggregation_strategy",
    "execution_trace",
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

    d = record["budget_declared"]
    c = record["budget_consumed"]
    for k in ("max_calls", "max_output_tokens", "max_wall_seconds", "max_estimated_cost_usd"):
        if k not in d:
            raise ValueError(f"budget declaration missing {k}")

    if c.get("calls", 0) > d["max_calls"]:
        raise ValueError("call budget exceeded")
    if c.get("output_tokens", 0) > d["max_output_tokens"]:
        raise ValueError("token budget exceeded")
    if c.get("wall_seconds", 0) > d["max_wall_seconds"]:
        raise ValueError("wall-clock budget exceeded")
    if c.get("estimated_cost_usd", 0) > d["max_estimated_cost_usd"]:
        raise ValueError("cost budget exceeded")

    trace = record["execution_trace"]
    if not isinstance(trace, list):
        raise ValueError("execution_trace must be a list")

    required_trace_fields = {
        "condition",
        "model_role",
        "semantic_role",
        "model_id",
        "seed",
        "round",
        "order",
        "prompt_version",
        "input_tokens",
        "output_tokens",
        "latency_seconds",
        "estimated_cost_usd",
    }
    for event in trace:
        if event.get("event") == "model_call":
            missing_trace = required_trace_fields - set(event)
            if missing_trace:
                raise ValueError(
                    f"model trace missing {sorted(missing_trace)}"
                )
