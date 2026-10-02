import os,time
class OpenAIAdapter:
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"): raise RuntimeError("OPENAI_API_KEY is required")
        try: from openai import OpenAI
        except ImportError as e: raise RuntimeError("install optional dependency: pip install -e '.[real]'") from e
        self.client=OpenAI()
    def generate(self,*,prompt,system_prompt,model_id,temperature,top_p,max_tokens,seed):
        start=time.monotonic()
        r=self.client.chat.completions.create(model=model_id,messages=[{"role":"system","content":system_prompt},{"role":"user","content":prompt}],temperature=temperature,top_p=top_p,max_tokens=max_tokens,seed=seed)
        u=r.usage
        return type("GenerationResult",(),{"text":r.choices[0].message.content or "","input_tokens":getattr(u,"prompt_tokens",0) if u else 0,"output_tokens":getattr(u,"completion_tokens",0) if u else 0,"latency_seconds":time.monotonic()-start,"model_id":model_id})()
