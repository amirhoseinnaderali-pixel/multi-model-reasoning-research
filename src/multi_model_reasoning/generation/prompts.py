from pathlib import Path
import hashlib
class PromptRegistry:
    def __init__(self,root): self.root=Path(root)
    def load(self,filename):
        text=(self.root/filename).read_text(encoding="utf-8")
        return text,hashlib.sha256(text.encode()).hexdigest()
