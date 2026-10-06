import shutil,subprocess,tempfile,time
from .result import VerificationResult,Verdict
class DockerUnavailable(RuntimeError): pass
class DockerPythonVerifier:
    def __init__(self,image):
        if shutil.which("docker") is None: raise DockerUnavailable("docker CLI unavailable")
        self.image=image
    def verify(self,code,test_source,timeout_seconds=10.0):
        started=time.monotonic()
        with tempfile.TemporaryDirectory() as td:
            open(td+"/candidate.py","w").write(code); open(td+"/tests.py","w").write(test_source)
            try:
                p=subprocess.run(["docker","run","--rm","--network","none","--cap-drop","ALL","--security-opt","no-new-privileges","--read-only","-v",f"{td}:/work:ro",self.image,"python","/work/tests.py"],capture_output=True,text=True,timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                return VerificationResult(Verdict.TIMEOUT,0,0,time.monotonic()-started,"execution timeout")
            except Exception as e:
                return VerificationResult(Verdict.INFRA_FAILURE,0,0,time.monotonic()-started,str(e))
            if p.returncode==0:return VerificationResult(Verdict.PASS,1,1,time.monotonic()-started)
            return VerificationResult(Verdict.WRONG,0,1,time.monotonic()-started,p.stderr[-4000:])
