import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "composition_driver", Path(__file__).with_name("driver.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_tasks_have_paired_prompts_and_context_hashes():
    frozen, tasks = module.make_spec()
    assert len(frozen["plan"]) == 48
    assert len(tasks) == 12
    for row in frozen["plan"]:
        task = tasks[row["task_name"]]
        original = module.role.with_prompt(task, "original_child")
        trained = module.role.with_prompt(task, "sft_child")
        assert original.hash == trained.hash == row["task_hash"]
        assert original.data.prompt == trained.data.prompt
        assert task.data.context.count(" || Instance: ") == 64
        assert task.data.answer_type == "ANSWER_TYPE.NUMERIC"
        assert task.data.context_len > 0
        assert (
            __import__("hashlib").sha256(task.data.context.encode()).hexdigest()
            == row["context_sha256"]
        )
