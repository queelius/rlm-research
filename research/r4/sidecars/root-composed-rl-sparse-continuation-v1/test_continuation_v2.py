import subprocess


def test_v2_uses_existing_qualified_training_python():
    import continuation_study_v2 as study

    assert study.TRAIN.exists()
    assert str(study.TRAIN).endswith("gpu/training/.venv/bin/python")


def test_actual_training_python_imports_v2_and_sparse_dependencies():
    import continuation_study_v2 as study

    command = [str(study.TRAIN), "-c",
               "import continuation_train_v2 as t; print(t.runtime_preflight()['torch'])"]
    result = subprocess.run(command, check=True, text=True, capture_output=True, timeout=30)
    assert result.stdout.strip() == "2.13.0+cu130"


def test_v2_owner_routes_trainer_to_v2_entry():
    import continuation_owner_v2 as owner
    import continuation_study_v2 as study

    argv = owner.trainer_argv(__import__("pathlib").Path("/stage"), {},
                              {"path": "/checkpoint"}, 12.0)
    assert argv[0] == str(study.TRAIN)
    assert argv[1] == str(study.ROOT / "continuation_train_v2.py")
