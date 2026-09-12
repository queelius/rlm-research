"""Authenticate four fixed checkpoints without consulting new-panel or seed2 eval outcomes."""

import hashlib
from pathlib import Path

import study

SOURCE = study.SOURCE / "eligibility.py"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != "b62864f9331f4794a4940ec8cc08460a64688c9ab16cede568f251c826bc68c8":
    raise ValueError("eligibility source changed")
exec(compile(raw, str(SOURCE), "exec"), globals())
_base_qualify = qualify

SEED2_QUALIFIED = study.SIDE.parent / "operations/2026-09-12-seed2-fixed512-queue/QUALIFIED.json"
SEED2_QUALIFIED_SHA = "4e5a09a527e735e0ba0920e1223407c476a37fb08445b7abfd7559e2a774e9b3"
SEED2_TRAIN = study.SIDE / "helper-agnews-native-hf-eightstep-seed2-v1"
SEED2_TRAIN_READY_SHA = "abafc45c35a038aee97ccb7a4dce4dee8c2ce03b111a9430bd2c17022ac20853"


def seed2_endpoint():
    if study.sha(SEED2_QUALIFIED) != SEED2_QUALIFIED_SHA or study.sha(SEED2_TRAIN / "READY.json") != SEED2_TRAIN_READY_SHA:
        raise ValueError("seed2 completed qualification source changed")
    receipt = study.read(SEED2_QUALIFIED)
    checkpoint = Path(receipt["checkpoint"])
    binding = receipt["binding"]
    child = binding["models"][study.CHILD_ALIAS]
    final = study.read(SEED2_TRAIN / "outputs/attempt-001/FINAL_RESULT.json")
    if (
        receipt.get("eligible") is not True
        or receipt.get("arm") != "rl_seed2_step8"
        or receipt.get("selection") != "none; fixed completed step8"
        or child.get("path") != str(checkpoint)
        or child.get("adapter_sha256") != study.sha(checkpoint / "adapter_model.safetensors")
        or child.get("config_sha256") != study.sha(checkpoint / "adapter_config.json")
        or receipt.get("state_sha256") != study.sha(checkpoint / "state.json")
        or receipt.get("step_commit_sha256") != study.sha(checkpoint / "STEP_COMMIT.json")
        or final.get("status") != "UPDATED_STEP8"
        or final.get("completed_steps") != 8
        or final.get("primary_endpoint_eligible") is not True
        or final.get("heldout_model_calls") != 0
    ):
        raise ValueError("seed2 exact qualified completed checkpoint differs")
    return receipt


def qualify(arm):
    if arm == "rl_seed2_step8":
        return seed2_endpoint()
    if arm in ("c32", "rl_step8", "sft_step8"):
        receipt = _base_qualify(arm)
        if arm == "c32":
            checkpoint = Path(receipt["checkpoint"])
            receipt["state_sha256"] = study.sha(checkpoint / "state.json")
            receipt["binding_sha256"] = study.digest(receipt["binding"])
        return receipt
    raise ValueError("unknown endpoint arm")


def fixed_endpoints(arm):
    path = study.ROOT / "ENDPOINTS_FIXED.json"
    receipt = study.read(path)
    if (
        receipt.get("authority") != "MAIN"
        or receipt.get("new_panel_model_calls_before_fix") != 0
        or receipt.get("seed2_exposed_panel_score_consulted_before_fix") is not False
        or receipt.get("evaluation_data_ready_sha256") != study.sha(study.EVAL_DATA / "DATA_READY.json")
        or set(receipt.get("trained_endpoints", {})) != set(study.ARMS)
    ):
        raise ValueError("four endpoints were not predeclared before new-panel queries")
    current = qualify(arm)
    for name, expected in ((arm, receipt["trained_endpoints"][arm]),):
        for key in ("checkpoint", "state_sha256", "binding_sha256"):
            if current.get(key) != expected.get(key):
                raise ValueError("fixed endpoint changed: " + name + ":" + key)
        if name != "c32" and current.get("step_commit_sha256") != expected.get("step_commit_sha256"):
            raise ValueError("fixed step commit changed: " + name)
    return {
        "fixed_receipt_path": str(path),
        "fixed_receipt_sha256": study.sha(path),
        "selected_endpoints": receipt["trained_endpoints"],
        "arm_eligibility": current,
        "evaluation_inputs": {
            "path": str(study.EVAL_DATA / "DATA_READY.json"),
            "sha256": study.sha(study.EVAL_DATA / "DATA_READY.json"),
        },
        "checkpoint_training_inputs_separate_from_evaluation_inputs": True,
    }
