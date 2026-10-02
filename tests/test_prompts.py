from multi_model_reasoning.generation.prompts import PromptRegistry
def test_prompt_hash(tmp_path):
    p=tmp_path/"p.txt";p.write_text("hello");text,h=PromptRegistry(tmp_path).load("p.txt");assert text=="hello" and len(h)==64
