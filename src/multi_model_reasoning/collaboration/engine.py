from .protocols import StrategySpec
from ..aggregation.voting import deterministic_majority

class CollaborationEngine:
    """Explicit protocol executor; round visibility is encoded in prompts."""
    def __init__(self,adapters,budget): self.adapters=adapters; self.budget=budget
    def _generate(self,role,prompt,system_prompt,generation_kwargs):
        max_tokens=generation_kwargs["max_tokens"]
        self.budget.reserve_call(requested_output_tokens=max_tokens,worst_case_seconds=generation_kwargs.get("worst_case_seconds",0.0),estimated_cost_usd=generation_kwargs.get("worst_case_cost_usd",0.0))
        try:
            res=self.adapters[role].generate(prompt=prompt,system_prompt=system_prompt,**{k:v for k,v in generation_kwargs.items() if k not in {"worst_case_seconds","worst_case_cost_usd"}})
            self.budget.settle_call(actual_output_tokens=res.output_tokens,actual_wall_seconds=res.latency_seconds,reserved_output_tokens=max_tokens,reserved_wall_seconds=generation_kwargs.get("worst_case_seconds",0.0),reserved_cost_usd=generation_kwargs.get("worst_case_cost_usd",0.0))
            return res
        except Exception:
            self.budget.settle_call(actual_output_tokens=0,reserved_output_tokens=max_tokens,reserved_wall_seconds=generation_kwargs.get("worst_case_seconds",0.0),reserved_cost_usd=generation_kwargs.get("worst_case_cost_usd",0.0))
            raise
    def run(self,*,spec,problem,system_prompt,generation_kwargs,verifier=None):
        outputs=[]
        if spec.condition in {"C0","C1","C2"}:
            roles=list(spec.model_pool) if spec.condition=="C2" else [spec.model_pool[0]]*spec.calls_per_task
            for role in roles: outputs.append(self._generate(role,problem,system_prompt,generation_kwargs))
            final=outputs[0].text if spec.condition=="C0" else deterministic_majority([x.text for x in outputs])
        elif spec.condition=="C3":
            a=self._generate("A",problem,system_prompt,generation_kwargs)
            b=self._generate("B",problem+"\n\nCANDIDATE:\n"+a.text,system_prompt,generation_kwargs)
            c=self._generate("A",problem+"\n\nCANDIDATE:\n"+a.text+"\n\nCRITIQUE:\n"+b.text,system_prompt,generation_kwargs)
            outputs=[a,b,c]; final=c.text
        elif spec.condition in {"C4","C5","C6"}:
            context=problem
            for role in spec.model_pool:
                res=self._generate(role,context,system_prompt,generation_kwargs); outputs.append(res); context+="\n\nPREVIOUS OUTPUT:\n"+res.text
            if spec.condition=="C6":
                if verifier is None or not hasattr(verifier,"select_visible"): raise RuntimeError("C6 requires independent objective verifier")
                final=verifier.select_visible([x.text for x in outputs])
            else: final=outputs[-1].text
        else: raise ValueError(spec.condition)
        return final,outputs
