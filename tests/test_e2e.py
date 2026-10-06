import subprocess,sys
def test_end_to_end_validation():
    p=subprocess.run([sys.executable,"scripts/run_experiment.py","--config","configs/experiments/exp001_fixed_budget.json","--mode","validation_only"],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
