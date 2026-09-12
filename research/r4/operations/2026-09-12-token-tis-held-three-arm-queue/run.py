"""MAIN admitted all fixed RL doses; external shared GPU flock required."""

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-12-rl-perturbation-chain/run.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347":
    raise ValueError("reviewed driver changed")
spec = importlib.util.spec_from_file_location("token_tis_held_driver", SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / "openai-mrcr-short-root-token-tis-held-eval-v1"
READY = SIDE / "CPU_READY_V4.json"
EXPECTED = "fb703d787841976e04a016e69e95841e1aa1ab4003840b0d4afb2cd0f8a0c65d"


if __name__ == "__main__":
    if driver.sha(READY) != EXPECTED:
        raise ValueError("reviewed V4 READY changed")
    original = driver.read(READY)
    if original["stage_order"] != ["base", "lr1e-5", "lr1e-4"]:
        raise ValueError("retain all fixed arms in frozen order")
    driver.STAGES = []
    for stage in original["stage_order"]:
        if (SIDE / "outputs-v4" / (stage + "-001")).exists():
            raise ValueError("preserve existing fixed-arm output")
        closure = dict(original["closure_sha256"])
        closure[str(READY)] = EXPECTED
        value = {"schema": "main-fixed-stage-command-binding-v1", "parent_ready_sha256": EXPECTED,
                 "parent_ready_identity": original["identity"], "stage": stage,
                 "command": original["stage_argv"][stage], "closure_sha256": closure}
        value["identity"] = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        filename = "READY_" + stage + ".json"
        driver.write_once(filename, value)
        driver.STAGES.append((stage, str(ROOT), filename, driver.sha(ROOT / filename), 700, True))
    driver.write_once("ADMISSION.json", {
        "authority": "MAIN", "epoch": driver.time.time(),
        "decision": "APPROVE_ALL_THREE_FIXED_TOKEN_TIS_HELD_ARMS",
        "wrapper_sha256": driver.sha(__file__), "ready_sha256": EXPECTED,
        "question": "Does a verified ten-times-larger independent RL update improve answers on conversations not used for its gradient?",
        "review": "MAIN read V4 and inherited owner/study/collector/checkpoint seams and actual test fixtures; own unmocked verify passed. Independent local_rl_design review reproduced4tests, initial/gradient and both actual Adam/state/commit links; no material blocker.",
        "episodes_per_arm": 16, "paired_contexts": 16, "owner_seconds_each": 650,
        "external_seconds_each": 700, "checkpoint_selection": False,
        "checkpoint_policy": "Persist each physical call, episode and terminal; no retries or missing-as-wrong replacement.",
        "prior_exposure_correction": "Parent READY overstates procedural-SFT held evaluation: cp4 train gate failed, so that conditional held phase made no queries. The earlier shaped-RL held dependency also failed before queries. This remains an exploratory reused frozen panel, not a confirmatory claim.",
        "bias_boundary": "Both doses use the declared biased detached token-TIS surrogate. Native answer evaluation is distinct from training-backend likelihood movement.",
    })
    driver.main()
