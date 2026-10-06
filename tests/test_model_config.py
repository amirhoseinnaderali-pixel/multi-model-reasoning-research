from multi_model_reasoning.models.config import ModelConfig
def test_model_config_hash_is_deterministic():
    c=ModelConfig("x","m","v",0,1,10,42,"p")
    assert c.config_hash()==c.config_hash()
