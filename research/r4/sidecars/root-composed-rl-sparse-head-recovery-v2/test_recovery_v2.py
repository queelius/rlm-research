import recovery2_owner as owner
import recovery2_study as study

def test_requalification_is_fixed_and_passes():
    value=study.verify_requalification()
    assert value["passed"] is True
    assert value["post_diagnostic_engineering_thresholds"]=={"gradient_relative_l2_max":.03,"gradient_cosine_min":.9995,"sparse_difference_vs_repeat_ratio_max":2.0}
    assert value["optimizer_steps"]==0

def test_owner_runs_exact_old_trainer_and_budget():
    argv=owner.training_argv(__import__('pathlib').Path('/out'),123.0)
    assert argv[1]==str(study.V1/"sparse_train.py")
    assert argv[-2:]==["--deadline","123.0"]
    assert owner.budget(10)=={"started":10,"work":1810,"owned":2080,"outer":2110}
