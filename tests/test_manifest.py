from multi_model_reasoning.logging.manifest import hash_json
def test_manifest_hash_is_order_invariant():
    assert hash_json({"a":1,"b":2})==hash_json({"b":2,"a":1})
