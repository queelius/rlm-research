"""CPU-only audit of owner -> fresh collector -> exporter and ownership accounting."""

import dis
import json
import os
from pathlib import Path
import subprocess
import time

import collect_v3
import owner_v3
import study


def main():
    constants = {item.argval for item in dis.get_instructions(owner_v3.execute)
                 if item.opname == "LOAD_CONST"}
    if "collect_v3.py" not in constants or "collect.py" in constants:
        raise ValueError("actual owner execute does not select the corrected fresh collector")
    script = (
        "import collect_v3 as c,study; c.activate(0,'no_child'); "
        "m=c.qualified.qualified.impl; assert m.verify_spec is c.verify_spec; "
        "r,a=m.s.runtime(); assert r.ROOT==study.ALLOCATION_RUNTIME; "
        "assert a.SERVICE==study.ALLOCATION_RUNTIME/'service_wrapper_v2.py'; "
        "table=c.terminal_study.read(study.SOURCE_INPUTS/'TASKS.json'); "
        "row=study.make_blocks()[0][0]; public={v['id']:v for v in study.read(study.SOURCE_INPUTS/'PUBLIC.json')}; "
        "gold=study.read(study.SOURCE_INPUTS/'HOST_GOLD.json'); "
        "task=c.make_task(public[row['context_id']],row['question'],gold[row['context_id']]['answers'][row['family']],row['task_name']); "
        "assert task.hash==table[row['task_name']]['task_hash']; "
        "assert c.first_prefix(task)==table[row['task_name']]['first_prompt_token_ids']; "
        "import terminal_export; assert terminal_export.qualified.rebuild.__globals__['s'].read is c._read; "
        "assert terminal_export.qualified.metrics.endpoint.__globals__['s'].read is c._read"
    )
    result = subprocess.run([str(study.NATIVE), "-c", script], cwd=study.ROOT,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1",
             "STRICT_RLM_CALIBRATION_API_KEY": "cpu-structure-only"},
        capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    reference = study.REFERENCE / "outputs/attempt-001/collection/rollout"
    typed = len(list((reference / "typed-audit").glob("*-request.json")))
    roles = len(list((reference / "role-audit").glob("*-request.json")))
    status = study.read(reference / "STATUS.json")["physical_attempts"]
    if (typed, roles, status) != (230, 230, 230):
        raise ValueError("historical physical request audit no longer has exact parity")
    receipt = {
        "schema": "root-qs6-recursion-headroom-cpu-path-audit-v3",
        "created_epoch": time.time(), "gpu_calls": 0,
        "owner_execute_collector": "collect_v3.py", "fresh_process_returncode": result.returncode,
        "fresh_process_runtime": str(study.ALLOCATION_RUNTIME),
        "fresh_process_tasks_hash_prefix": True, "fresh_process_export_metrics_read": True,
        "historical_physical_request_parity": {"typed": typed, "role": roles,
                                                "status_physical_attempts": status},
        "expired_cleanup_alarm_rearmed_to_point001": False,
        "expired_cleanup_behavior": "record failure, disable nested alarm, attempt release under 1900s external cap",
    }
    study.write(study.ROOT / "CPU_PATH_AUDIT_V3_FINAL.json", receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
