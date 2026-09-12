"""MAIN admission/bootstrap; the sealed operation itself owns the shared flock."""

import hashlib
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent
READY = ROOT / "READY.json"
if hashlib.sha256(READY.read_bytes()).hexdigest() != "48beb204e9ee1988959a6052aa38430d0c2b34213abf2ffdd2b56573f2182552":
    raise ValueError("reviewed operation READY changed")
ready = json.loads(READY.read_text())
for raw, expected in ready["closure_sha256"].items():
    if hashlib.sha256(Path(raw).read_bytes()).hexdigest() != expected:
        raise ValueError("operation closure changed: " + raw)
with (ROOT / "MAIN_ADMISSION.json").open("x") as stream:
    json.dump({
        "authority": "MAIN", "decision": "APPROVE_FIXED4_PROCEDURAL_SFT_AND_CONDITIONAL_READOUT",
        "epoch": time.time(), "operation_ready_sha256": hashlib.sha256(READY.read_bytes()).hexdigest(),
        "review": "Training/teacher and evaluator sources fully reviewed, actual teacher-container two-prefix fixture read, evaluator five focused tests and operation four tests read. Own evaluator138-pin verify and exact operation dependency check passed.",
        "question": "Can32 demonstrations teach an exact retrieval/copy routine that works on different conversations?",
        "training": "Fixed four full-batch updates, root only, base child unchanged; checkpoint Adam/RNG/adapter each step.",
        "evaluation": "Fixed checkpoint4 on train32; only after all32 available and8 raw-exact across4 contexts evaluate held16x2 for both base andcheckpoint4. No other checkpoint selection.",
        "locks": "Operation run.py acquires shared fcntl.flock itself; do NOT wrap this bootstrap in a second flock.",
        "caps": {"queue_seconds": 14400, "science_seconds_after_lock": 4200},
        "limits": "A demonstrated retrieval routine is not autonomous planning or learned recursion. Held conversations also serve a prospectively specified separate root-RL comparison; local exploratory evaluation, not untouched pretraining data.",
    }, stream, indent=2, sort_keys=True)
    stream.write("\n")
environment = dict(os.environ)
environment.update(
    CUDA_VISIBLE_DEVICES="MIG-c0ac02b2-b43f-58cf-ab06-dc24b64b023a",
    OMP_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1",
)
environment["PATH"] = "/export/software/system/nvidia/580.126.20/bin:" + environment.get("PATH", "")
environment["LD_LIBRARY_PATH"] = "/export/software/system/nvidia/580.126.20/lib:" + environment.get("LD_LIBRARY_PATH", "")
private = ROOT.parents[1] / "sidecars/leaf-output-cue-order-v1/owned/attempt-001/service/inference.json"
environment["STRICT_RLM_CALIBRATION_API_KEY"] = json.loads(private.read_text())["vllm"]["api_key"][0]
os.execvpe(ready["fixed_argv"][0], ready["fixed_argv"], environment)
