from dataclasses import dataclass, asdict

class BudgetExceeded(RuntimeError):
    pass

@dataclass
class Budget:
    max_calls: int
    max_output_tokens: int
    max_wall_seconds: float
    max_estimated_cost_usd: float
    calls: int = 0
    output_tokens: int = 0
    wall_seconds: float = 0.0
    estimated_cost_usd: float = 0.0
    reserved_output_tokens: int = 0
    reserved_cost_usd: float = 0.0
    reserved_wall_seconds: float = 0.0

    def reserve_call(self, *, requested_output_tokens, estimated_cost_usd=0.0, worst_case_seconds=0.0):
        if self.calls + 1 > self.max_calls: raise BudgetExceeded("call budget exceeded")
        if self.output_tokens + self.reserved_output_tokens + requested_output_tokens > self.max_output_tokens: raise BudgetExceeded("token budget exceeded before generation")
        if self.wall_seconds + self.reserved_wall_seconds + worst_case_seconds > self.max_wall_seconds: raise BudgetExceeded("wall-clock budget exceeded before generation")
        if self.estimated_cost_usd + self.reserved_cost_usd + estimated_cost_usd > self.max_estimated_cost_usd: raise BudgetExceeded("cost budget exceeded before generation")
        self.calls += 1
        self.reserved_output_tokens += requested_output_tokens
        self.reserved_cost_usd += estimated_cost_usd
        self.reserved_wall_seconds += worst_case_seconds

    def settle_call(self, *, actual_output_tokens, actual_cost_usd=0.0, actual_wall_seconds=0.0, reserved_output_tokens, reserved_cost_usd=0.0, reserved_wall_seconds=0.0):
        self.reserved_output_tokens -= reserved_output_tokens
        self.reserved_cost_usd -= reserved_cost_usd
        self.reserved_wall_seconds -= reserved_wall_seconds
        self.output_tokens += actual_output_tokens
        self.estimated_cost_usd += actual_cost_usd
        self.wall_seconds += actual_wall_seconds
        if self.output_tokens > self.max_output_tokens or self.wall_seconds > self.max_wall_seconds or self.estimated_cost_usd > self.max_estimated_cost_usd:
            raise BudgetExceeded("actual usage exceeded declared budget")

    def snapshot(self): return asdict(self)
