from .sandbox import DockerPythonVerifier
class CandidateVerifier:
    def __init__(self,image,visible_tests,hidden_tests,timeout_seconds=10.0):
        self.verifier=DockerPythonVerifier(image); self.visible_tests=visible_tests; self.hidden_tests=hidden_tests; self.timeout_seconds=timeout_seconds
    def select_visible(self,candidates):
        scores=[]
        for c in candidates:
            r=self.verifier.verify(c,self.visible_tests,self.timeout_seconds)
            if r.verdict.value=="infrastructure_failure": raise RuntimeError(r.message)
            scores.append((r.passed_tests,-r.latency_seconds,c))
        return max(scores,key=lambda x:(x[0],x[1]))[2]
    def verify_hidden(self,candidate):
        return self.verifier.verify(candidate,self.hidden_tests,self.timeout_seconds)
