import dis
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).parent


def test_actual_owner_execute_launches_v2_collector_and_v3_ready():
    import owner_v3
    import study_v3

    constants = {value for instruction in dis.get_instructions(owner_v3.execute)
                 if instruction.opname == "LOAD_CONST" for value in [instruction.argval]}
    assert "collect_v3.py" in constants
    assert "collect.py" not in constants
    assert owner_v3.execute.__globals__["physical_request_audit"] is owner_v3.physical_request_audit
    assert owner_v3.execute.__globals__["_arm_cleanup"] is owner_v3._arm_cleanup
    check = subprocess.run(
        [sys.executable, "-c",
         "import collect_v3 as c, owner_v3, study; "
         "c.activate(0,'no_child'); table=c.terminal_study.read(study.SOURCE_INPUTS/'TASKS.json'); "
         "row=study.make_blocks()[0][0]; "
         "public={v['id']:v for v in study.read(study.SOURCE_INPUTS/'PUBLIC.json')}; "
         "gold=study.read(study.SOURCE_INPUTS/'HOST_GOLD.json'); "
         "task=c.make_task(public[row['context_id']],row['question'],gold[row['context_id']]['answers'][row['family']],row['task_name']); "
         "assert task.hash==table[row['task_name']]['task_hash']; "
         "assert c.first_prefix(task)==table[row['task_name']]['first_prompt_token_ids']; "
         "import terminal_export; "
         "assert terminal_export.qualified.rebuild.__globals__['s'].read is c._read; "
         "assert terminal_export.qualified.metrics.endpoint.__globals__['s'].read is c._read"],
        cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert check.returncode == 0, check.stdout + check.stderr


def test_request_counter_and_expired_cleanup_alarm_are_truthful(tmp_path):
    import owner_v3

    rollout = tmp_path / "blocks/00-no_child/collection/rollout"
    for directory in ("typed-audit", "role-audit"):
        (rollout / directory).mkdir(parents=True)
        for index in range(3):
            (rollout / directory / f"{index}-request.json").write_text("{}")
    (rollout / "STATUS.json").write_text(json.dumps({"physical_attempts": 3}))
    assert owner_v3.physical_request_count(tmp_path) == 3
    assert owner_v3.cleanup_alarm_seconds(100.0, 90.0) == 10.0
    assert owner_v3.cleanup_alarm_seconds(100.0, 100.1) is None
    (rollout / "role-audit/2-request.json").unlink()
    try:
        owner_v3.physical_request_count(tmp_path)
    except ValueError as error:
        assert "typed/role" in str(error)
    else:
        raise AssertionError("request-audit mismatch accepted")
