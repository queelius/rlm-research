import arm_eval_study_v3 as study


def test_zero_argument_collector_verify_resolves_selected_arm():
 study.select("t2_lr1e5")
 assert study.resolve_arm()=="t2_lr1e5"
