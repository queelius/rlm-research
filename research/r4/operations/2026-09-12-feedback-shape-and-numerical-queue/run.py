"""Reviewed reward-baseline recovery, inference-shape check, and numerical budget test."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
SOURCE_SHA = "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("reviewed_feedback_shape_queue", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
driver.STAGES = [
    ("paired_repair_train", "helper-hf-onpolicy-other31-paired-onestep-v2", "READY.json",
     "e33c3f849abef8f05b7a09c3315980befe890ca8983b094294f1d0ce3be39807", 2850, False),
    ("paired_rloo_eval", "helper-hf-onpolicy-other31-paired-unseen-eval-v2", "READY_RLOO.json",
     "eac5001d433ac17f1fea6150dd34fb6c663f15c88468fe68760e6b89d0a3144e", 700, True),
    ("paired_other31_eval", "helper-hf-onpolicy-other31-paired-unseen-eval-v2", "READY_OTHER31.json",
     "5d828f62060ba4d7645c93bf584a304642322bf5d94d4ae0dd5133ac6a2eb7d2", 700, True),
    ("singleton_c32", "helper-hf-singleton-policy-comparison-v1", "READY_C32.json",
     "6fdc78f32cc82c17f39b40028e9d0537189f125641a0de9005bcf7fd61631d40", 1000, True),
    ("singleton_reference", "helper-hf-singleton-policy-comparison-v1", "READY_REFERENCE_STEP4.json",
     "3db17d9d5fb9d2383ff683efd0906334bf1a6773d1354dcd397bc16696e1d2dd", 1000, True),
    ("numerical_budget_shape", "anomalyxl-native-budget-shape-v2", "READY.json",
     "88a6758c061389c714c3c7b73745164fecbda01fb9a9579caec15dd641dabb77", 1900, False),
]
OUTPUTS = [
    "helper-hf-onpolicy-other31-paired-onestep-v2/outputs/attempt-001",
    "helper-hf-onpolicy-other31-paired-unseen-eval-v2/arms/rloo/outputs/attempt-001",
    "helper-hf-onpolicy-other31-paired-unseen-eval-v2/arms/other31/outputs/attempt-001",
    "helper-hf-singleton-policy-comparison-v1/outputs/c32/attempt-001",
    "helper-hf-singleton-policy-comparison-v1/outputs/reference_step4/attempt-001",
    "anomalyxl-native-budget-shape-v2/outputs/attempt-001",
]

if __name__ == "__main__":
    for path in OUTPUTS:
        if (driver.SIDES / path).exists():
            raise ValueError("preserve existing output: " + path)
    driver.write_once("WRAPPER_START.json", {
        "wrapper_sha256": driver.sha(__file__), "driver_sha256": SOURCE_SHA,
        "started_epoch": driver.time.time(),
        "paired_sampling": "128 exact committed source actions reused; no new collection",
        "independent_successors": ["singleton_c32", "singleton_reference", "numerical_budget_shape"],
        "numerical_inventory": "70 planned maximum research calls; owner admission limit80; two engineering",
    })
    driver.main()
