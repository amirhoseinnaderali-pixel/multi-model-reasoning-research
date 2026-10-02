from dataclasses import dataclass

@dataclass(frozen=True)
class StrategySpec:
    condition: str
    name: str
    description: str
    calls_per_task: int
    rounds: int
    model_pool: tuple[str, ...]
    semantic_roles: tuple[str, ...]
    uses_verifier: bool
    aggregation: str

SPECS = {
    "C0": StrategySpec("C0", "single_model", "one generation", 1, 1, ("A",), ("solver",), False, "identity"),
    "C1": StrategySpec(
        "C1", "independent_multi_sample",
        "three independent samples from the same model, selected by visible objective verification",
        3, 1, ("A",), ("solver",), True, "visible_objective_selection"
    ),
    "C2": StrategySpec(
        "C2", "independent_multi_model",
        "three independent solutions from different model roles, selected by visible objective verification",
        3, 1, ("A", "B", "C"), ("solver", "solver", "solver"), True, "visible_objective_selection"
    ),
    "C3": StrategySpec("C3", "debate_critique", "solver, critic, solver revision", 3, 2, ("A", "B"), ("solver", "critic"), False, "final"),
    "C4": StrategySpec("C4", "sequential_refinement", "A then B then C refinement", 3, 3, ("A", "B", "C"), ("solver", "solver", "solver"), False, "final"),
    "C5": StrategySpec(
        "C5", "role_specialized",
        "explicit solver, critic, verifier, synthesizer protocol with role-specific prompts and controlled information visibility",
        4, 4, ("A", "B", "C", "D"),
        ("solver", "critic", "verifier", "synthesizer"), False, "role_specialized_final"
    ),
    "C6": StrategySpec(
        "C6", "collaborative_refinement_verified",
        "sequential solver -> critic/refinement -> synthesizer, followed by independent visible-test candidate selection",
        3, 3, ("A", "B", "C"),
        ("solver", "critic", "synthesizer"), True, "sequential_refinement_visible_selection"
    ),
}

def get_strategy(condition):
    if condition not in SPECS:
        raise KeyError(condition)
    return SPECS[condition]
