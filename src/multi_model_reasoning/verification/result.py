from dataclasses import dataclass
from enum import Enum
class Verdict(str,Enum):
    PASS="pass"; WRONG="wrong_answer"; TIMEOUT="timeout"; MALFORMED="malformed_output"; MODEL_FAILURE="model_failure"; INFRA_FAILURE="infrastructure_failure"
@dataclass(frozen=True)
class VerificationResult:
    verdict: Verdict
    passed_tests: int
    total_tests: int
    latency_seconds: float
    message: str=""
