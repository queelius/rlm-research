"""The external object is the exact full `queries` field for each selected row."""

import asyncio
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def test_v3_preparation_freezes_eight_distinct_full_query_files(tmp_path):
    import study_v3

    result = study_v3.prepare_inputs(tmp_path)
    files = sorted((tmp_path / "full-queries").glob("*.txt"))
    assert len(files) == 8
    assert len({hashlib.sha256(path.read_bytes()).hexdigest() for path in files}) == 8
    assert result["underlying_contexts"] == 1
    assert result["full_query_files"] == 8
    tasks = study_v3.base.read(tmp_path / "tasks.json")
    assert len(tasks) == 32
    assert {task["document_sha256"] for task in tasks} == {path.stem for path in files}


def test_v3_task_setup_writes_exact_row_specific_full_query(tmp_path):
    import study_v3

    study_v3.prepare_inputs(tmp_path)
    study_v3.patch_task_setup(tmp_path)
    module = study_v3.base.old_module()
    task_data = study_v3.base.read(tmp_path / "tasks.json")[0]
    task = module.MRCRTask(module.MRCRData.model_validate(task_data))
    captured = {}
    class Runtime:
        async def write(self, path, value): captured[path] = value
        async def read(self, path): return captured[path]
    asyncio.run(task.setup(None, Runtime()))
    assert set(captured) == {"/context.txt"}
    assert hashlib.sha256(captured["/context.txt"]).hexdigest() == task.data.document_sha256
    source = tmp_path / "full-queries" / (task.data.document_sha256 + ".txt")
    assert captured["/context.txt"] == source.read_bytes()


def test_v3_collector_uses_unmounted_runtime_and_v3_inputs(tmp_path):
    import collect_v3
    import study_v3

    study_v3.prepare_inputs(tmp_path)
    env = collect_v3.environment(tmp_path)
    assert len(list(env.taskset)) == 32
    assert collect_v3.RUNTIME_BIN.name == "bin-v3"
    assert (collect_v3.RUNTIME_BIN / "docker").is_file()


def test_v3_owner_is_additive_attempt003():
    import owner_v3

    assert owner_v3.ATTEMPT == ROOT / "outputs/attempt-003"
    assert owner_v3.COLLECTOR == ROOT / "collect_v3.py"

