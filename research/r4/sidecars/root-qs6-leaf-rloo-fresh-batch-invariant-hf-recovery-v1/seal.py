"""Seal precomputed-mask HF-only recovery after both environments verify inputs."""

import json
import os
from pathlib import Path
import subprocess
import time

import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise ValueError("CPU-only seal requires hidden GPU")
    if (study.ROOT/"READY.json").exists():raise FileExistsError("READY exists")
    native=subprocess.run([str(study.NATIVE),"-m","pytest","-q","test_recovery.py"],cwd=study.ROOT,capture_output=True,text=True,timeout=30,env={**os.environ,"CUDA_VISIBLE_DEVICES":""})
    train=subprocess.run([str(study.TRAIN_PYTHON),str(study.ROOT/"score.py")],cwd=study.ROOT,capture_output=True,text=True,timeout=30,env={**os.environ,"CUDA_VISIBLE_DEVICES":""})
    study.write_x(study.ROOT/"CPU_TESTS.json",{"native":{"returncode":native.returncode,"stdout":native.stdout,"stderr":native.stderr},"training_environment":{"returncode":train.returncode,"stdout":train.stdout,"stderr":train.stderr},"xgrammar_installed_only_in_native":True})
    if native.returncode or train.returncode:raise ValueError("focused CPU qualification failed")
    files=list(study.ROOT.glob("*.py"))+[study.ROOT/"CPU_TESTS.json",study.ATTEMPT/"COLLECTION.json",study.ATTEMPT/"PREPARED.json",study.ATTEMPT/"SOURCE_INVENTORY.json",study.ATTEMPT/"qualification-inputs/DATASET.json",study.ATTEMPT/"qualification-inputs/MASK_MANIFEST.json",study.ATTEMPT/"qualification-inputs/MASKS.npz",study.SOURCE/"READY.json",study.SOURCE_ATTEMPT/"COLLECTION.json",study.SOURCE_ATTEMPT/"OWNER_TERMINAL.json",study.SOURCE_ATTEMPT/"service/SERVICE_STOPPED.json"]
    closure={str(path):study.sha(path) for path in files}
    value={"schema":"fresh-batch-invariant-hf-phase-recovery-ready-v1","status":"CPU_READY_HF_SCORE_ONLY","created_epoch":time.time(),"source_v2_ready_identity":"b27457638bfdeaae7b3edbbb12dddff44c0eb9b04a29287f50f3056bd960c346","source_v2_actions":48,"source_v2_recollected":False,"source_v1_raw_responses_reused":False,"native_service_started":False,"optimizer_steps":0,"prepared_masks_environment":"prime-rl native CPU with xgrammar","scoring_environment":"a100-lora training environment; consumes pinned masks without importing xgrammar","closure_sha256":closure,"command":[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--outer-seconds","360"],"cap_seconds":360,"external_timeout_seconds":420,"output":str(study.ATTEMPT),"pass_status":"QUALIFIED_NO_UPDATE","failure_status":"NO_UPDATE_LIKELIHOOD_GATE_FAILED","failure_action":"persist diagnostics without retry or optimizer step","claim_boundary":"Recovers only the HF scoring phase over the exact already-collected V2 fresh48 actions after clean native release; it is not a new batch, update authority, or HF/vLLM identity evidence.","cpu_tests":{"native":native.stdout.strip(),"training_environment":train.stdout.strip()}}
    value["identity"]=study.digest(value);study.write_x(study.ROOT/"READY.json",value);print(json.dumps({"ready_sha256":study.sha(study.ROOT/"READY.json"),"identity":value["identity"]},sort_keys=True))


if __name__=="__main__":main()
