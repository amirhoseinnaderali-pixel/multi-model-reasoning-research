from multi_model_reasoning.evaluation.statistics import paired_differences, paired_bootstrap_ci

def test_paired_difference_uses_task_seed_budget_keys():
    rows=[
        {"task_id":"t1","seed":1,"budget_id":"B1","condition":"C0","objective_verdict":"pass"},
        {"task_id":"t1","seed":1,"budget_id":"B1","condition":"C6","objective_verdict":"wrong_answer"},
        {"task_id":"t2","seed":1,"budget_id":"B1","condition":"C0","objective_verdict":"wrong_answer"},
        {"task_id":"t2","seed":1,"budget_id":"B1","condition":"C6","objective_verdict":"pass"},
    ]
    assert paired_differences(rows,"C6")==[-1,1]
    lo,hi=paired_bootstrap_ci([-1,1],n_boot=100,seed=7)
    assert lo<=hi

