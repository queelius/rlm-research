"""MAIN-reviewed fresh AG baseline, one-update pilot, and conditional readout."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("reviewed_ag_native_hf_queue", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
driver.STAGES = [
    ("ag_c32_baseline", "helper-agnews-heldout-eval-v1", "READY_C32_V2.json",
     "0233757687489e9adcd7c8cb0c8548abadba212ef3ba1a2528655e9884596768", 700, True),
    ("ag_native_hf_train", "helper-agnews-native-hf-onestep-v1", "READY.json",
     "9fa4df0e9921f35202abe0627914eda17be2851e089f7402c5f37d0830616be6", 1200, True),
    ("ag_native_hf_eval", "helper-agnews-native-hf-onestep-v1", "EVAL_READY.json",
     "d3caf49d6b4fa320c4e8116e33230f409b7077472156568531600049d6ca846b", 700, True),
]
OUTPUTS = [
    "helper-agnews-heldout-eval-v1/outputs/c32-001",
    "helper-agnews-native-hf-onestep-v1/outputs/attempt-001",
    "helper-agnews-native-hf-onestep-v1/eval/outputs/attempt-001",
]

if __name__ == "__main__":
    for path in OUTPUTS:
        if (driver.SIDES / path).exists():
            raise ValueError("preserve existing output: " + path)
    driver.write_once("WRAPPER_START.json", {
        "wrapper_sha256": driver.sha(__file__), "driver_sha256": SOURCE_SHA,
        "started_epoch": driver.time.time(),
        "training": "128 fresh AG records; 32 B4 requests x4 actions; one qualified update",
        "readout": "fixed disjoint AG256; fresh c32 versus exact qualified step1",
        "decision": "package exploration, not isolated factor or established gain",
        "preflight": "MAIN read all new source; exact native/mask and tiny HF fixtures passed; closures verified on CPU before lock",
    })
    driver.main()
