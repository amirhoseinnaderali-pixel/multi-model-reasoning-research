from multi_model_reasoning.evaluation.statistics import mean,median,bootstrap_ci
def test_stats():
    x=[0,1,1,0];assert mean(x)==.5 and median(x)==.5
    lo,hi=bootstrap_ci(x,n_boot=100,seed=1);assert 0<=lo<=hi<=1
