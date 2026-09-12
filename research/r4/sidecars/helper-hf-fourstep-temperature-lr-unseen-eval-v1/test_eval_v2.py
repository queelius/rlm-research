import arm_eval_study_v2 as study


def test_binding_experiment_names_are_exact_arm_roots():
 assert study.ARMS["t2_lr1e5"]["training_output"].parents[1].name=="t2-lr1e5"
 assert study.ARMS["t1_lr1e4"]["training_output"].parents[1].name=="t1-lr1e4"


def test_arm_states_remain_distinct():
 assert study.experimental_arm("t2_lr1e5")=={"name":"t2_lr1e5","temperature":2.0,"learning_rate":1e-5}
 assert study.experimental_arm("t1_lr1e4")=={"name":"t1_lr1e4","temperature":1.0,"learning_rate":1e-4}
