from dataclasses import dataclass

@dataclass(frozen=True)
class StrategySpec:
    condition: str
    name: str
    description: str
    calls_per_task: int
    rounds: int
    model_pool: tuple[str,...]
    uses_verifier: bool
    aggregation: str

SPECS={
"C0":StrategySpec("C0","single_model","one generation",1,1,("A",),False,"identity"),
"C1":StrategySpec("C1","independent_multi_sample","same model, independent samples",3,1,("A",),False,"majority"),
"C2":StrategySpec("C2","independent_multi_model","different models independently solve",3,1,("A","B","C"),False,"majority"),
"C3":StrategySpec("C3","debate_critique","solver, critic, solver revision",3,2,("A","B"),False,"final"),
"C4":StrategySpec("C4","sequential_refinement","A then B then C refinement",3,3,("A","B","C"),False,"final"),
"C5":StrategySpec("C5","role_specialized","solver, critic, verifier, synthesizer",4,4,("A","B","C","D"),False,"final"),
"C6":StrategySpec("C6","collaboration_verified","collaborative candidates with independent verifier",3,2,("A","B","C"),True,"verified_selection")
}

def get_strategy(condition):
    if condition not in SPECS: raise KeyError(condition)
    return SPECS[condition]
