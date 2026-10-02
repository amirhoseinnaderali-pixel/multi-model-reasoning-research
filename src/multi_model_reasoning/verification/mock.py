from types import SimpleNamespace
class MockVerifier:
    def select_visible(self,candidates): return candidates[0]
    def verify(self,candidate): return SimpleNamespace(verdict=SimpleNamespace(value="validation_only"))
