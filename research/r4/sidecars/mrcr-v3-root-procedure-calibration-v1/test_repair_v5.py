import inspect

import collect_v5
import study_v5


def test_actual_registered_task_class_gets_exact_full_query_setup_patch():
    env = collect_v5.environment(study_v5.INPUTS)
    tasks = list(env.taskset)
    assert len(tasks) == 32
    assert type(tasks[0]).__module__ == "mrcr_rootless_document_baseline_v2"
    assert inspect.getsourcefile(type(tasks[0]).setup) == str(study_v5.ROOT / "study_v5.py")
    assert {task.data.document_sha256 for task in tasks} == {
        row["queries_sha256"] for row in study_v5.full_rows()
    }


def test_v5_keeps_v4_runtime_and_exact_v3_science():
    assert study_v5.environment_config(study_v5.INPUTS) == study_v5.v4.environment_config(
        study_v5.INPUTS
    )
    assert study_v5.plan() == study_v5.base.plan()
    assert study_v5.ATTEMPT == study_v5.ROOT / "outputs/attempt-005"

