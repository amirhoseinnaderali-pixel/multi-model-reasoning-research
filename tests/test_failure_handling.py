from multi_model_reasoning.verification.result import Verdict,VerificationResult
def test_infrastructure_failure_is_distinct():
    r=VerificationResult(Verdict.INFRA_FAILURE,0,0,0.0,"docker unavailable")
    assert r.verdict is Verdict.INFRA_FAILURE
