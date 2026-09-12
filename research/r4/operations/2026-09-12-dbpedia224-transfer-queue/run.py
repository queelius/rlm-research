"""MAIN-reviewed four fixed helper endpoints on a different classification domain."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347":
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("dbpedia224_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "helper-dbpedia224-transfer-eval-v1"
driver.STAGES = [
    ("dbpedia_c32", SIDE.name, "READY_C32.json", "91ef16b7d649e3d0d7e78c708175e2373731189ae6445e1c2e80e1133260379c", 800, True),
    ("dbpedia_rl8", SIDE.name, "READY_RL_STEP8.json", "f754f0400904073e8266b51850de421c2091403e24ecb5f6185fe70ec448c5ca", 800, True),
    ("dbpedia_sft8", SIDE.name, "READY_SFT_STEP8.json", "c1e5efd4cccd4c9d376891ca2194117356cf31600be2e1be306b8d6b933b0cad", 800, True),
    ("dbpedia_rl8_seed2", SIDE.name, "READY_RL_SEED2_STEP8.json", "65905cf6f355f39ca6cd69fd0a37f95d15ff358669148df1bec6a4905890fabb", 800, True),
]

if __name__ == "__main__":
    if (SIDE / "outputs").exists():
        raise ValueError("preserve existing DBpedia output")
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "decision": "APPROVE_DBPEDIA224_FIXED_FOUR_ARMS",
        "epoch": driver.time.time(), "wrapper_sha256": driver.sha(__file__),
        "review": "All new source and actual raw-send/decoder/endpoint CPU fixtures read; own combined1454-pin source verify passed. MAIN authored and tested frozen data selection.",
        "question": "Do news-trained helper updates retain or improve performance in encyclopedia classification with14 different categories?",
        "records": 224, "records_per_class": 16, "calls_per_arm": 56,
        "caps": {"per_arm_owner_seconds": 700, "per_arm_external_seconds": 800},
        "fixed_arms": ["c32", "RL8seed1", "SFT8", "RL8seed2"],
        "selection": "No best seed/checkpoint. Frozen paired seeds202609123500..202609123555, T0/B4.",
        "limits": "New local dataset/domain/labelspace but still short-text classification, not broad reasoning or decomposition; pretraining exposure unknown. No new-model queries before fixed selection.",
        "followup": "Retain all four arms and class-specific differences. A raw-base reference is separate proposed work, not a replacement for any fixed arm.",
    })
    driver.main()
