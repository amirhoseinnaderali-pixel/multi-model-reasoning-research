from multi_model_reasoning.aggregation.voting import deterministic_majority
def test_deterministic_majority():assert deterministic_majority(["b","a","b","a","b"])=="b"
def test_tie_is_first_seen():assert deterministic_majority(["z","a"])=="z"
