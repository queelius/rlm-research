"""MAIN-approved semantic depth feasibility comparison; external flock required."""

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347":
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("musique_depth_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "musique-semantic-depth-pilot-v1"
READY = SIDE / "READY.json"
original_read = driver.read


def read_with_command(path):
    value = original_read(path)
    if Path(path).resolve() == READY.resolve():
        # The original READY and identity stay byte-for-byte unchanged. Only expose
        # its literal fixed argv under the existing driver's expected field name.
        return {**value, "command": value["fixed_argv"]}
    return value


driver.read = read_with_command
driver.STAGES = [
    ("musique_depth48", SIDE.name, "READY.json",
     "7907fdaea2177c6bd02bce0282c4e1423970c4a725a49432e1c905226a95bb34", 1800, True),
]

if __name__ == "__main__":
    if (SIDE / "outputs/attempt-001").exists():
        raise ValueError("preserve existing MuSiQue output")
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "decision": "APPROVE_MUSIQUE_OPTIONAL_DEPTH_FEASIBILITY",
        "epoch": driver.time.time(), "wrapper_sha256": driver.sha(__file__),
        "review": "All eight new sources, runbook and preserved fixture repair read; actual depth2/global-six/one-call/overlength CPU fixtures passed27.40s; own701-pin runtime verification passed.",
        "question": "Does allowing optional deeper delegation improve linked-fact question answering under the same total model-call ceiling?",
        "data": "Twelve frozen outcome-blind MuSiQue-Ans dev questions, four per2/3/4hop; all original paragraphs, no gold support/decomposition in runtime.",
        "arms": ["depth0", "depth1", "depth2", "question_only"],
        "episodes": 48, "primary": "depth2 versus depth0",
        "caps": {"physical_calls_per_primary_episode": 6, "output_tokens_per_call": 1024, "science_seconds": 1320, "owner_seconds": 1700, "external_seconds": 1800},
        "policy": "Released Qwen3-4B root and all children, no research adapter, paired seeds202609132000..202609132011, temperature0.5.",
        "claim_boundary": "Twelve question clusters, not48 independent tasks. Local dataset transfer is not pretraining novelty. Context can fit root after printing, so audit actual delegation and observation volume; no grandchild use cannot establish that deeper reasoning is ineffective.",
        "scoring": "Unchanged official answer/support metrics after strict JSON parsing; unknowns retained. Question-only is diagnostic, never an exclusion filter.",
        "next": "Interpret errors, actual chosen subtasks and context volume before proposing training, observation-budget or depth-policy follow-ons.",
    })
    driver.main()
