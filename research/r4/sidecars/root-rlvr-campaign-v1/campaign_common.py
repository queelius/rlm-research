"""Small immutable identity/checkpoint helpers for this one approved campaign."""

import hashlib
import importlib.util
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PILOT = ROOT.parent / "root-only-credit-v1"
ROLE = ROOT.parent / "leaf-role-routing-v1"
NATIVE_PYTHON = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
TRAIN_PYTHON = Path("/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python")
SEED = 981260800
CHILD_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
ORIGINAL_SHA = "857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6"
PILOT_SPEC_SHA = "bc38dadf55e6a45cd7c9a417cdafbc52a50494c3bfb6991752e7d0e500a8c4ed"
PILOT_RECIPE_SHA = "f1c226b08de69f29250efc69cc0634fd17db1ffd88c0f1ef0ab2edb8a91bdb96"
PILOT_TRAINER_SHA = "131bf68610ed54b102cb6aae4b0c73635877811d887039ea8ca4a3002c701a26"


def read(path):
    return json.loads(Path(path).read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def authenticate(hashes):
    for path, expected in hashes.items():
        if file_hash(path) != expected:
            raise ValueError(f"authenticated file changed: {path}")


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".pending-" + uuid.uuid4().hex)
    try:
        with temporary.open("x") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sample_seed(round_id, task_id, repeat):
    return int(digest([ROOT.name, SEED, round_id, task_id, repeat])[:8], 16) % (2**31 - 1)


def pilot_recipe():
    authenticate({PILOT / "TRAINING_RECIPE.json": PILOT_RECIPE_SHA,
                  PILOT / "source/train_root.py": PILOT_TRAINER_SHA,
                  PILOT / "SPEC.json": PILOT_SPEC_SHA})
    recipe = read(PILOT / "TRAINING_RECIPE.json")
    authenticate(recipe["authenticated_dependencies"])
    return recipe


def pilot_math():
    pilot_recipe()
    return load("campaign_authenticated_pilot_math", PILOT / "source/train_root.py")


def verify_campaign():
    manifest = read(ROOT / "CAMPAIGN.json")
    if digest({k: v for k, v in manifest.items() if k != "campaign_id"}) != manifest["campaign_id"]:
        raise ValueError("campaign manifest identity changed")
    authenticate(manifest["source_sha256"])
    authenticate(manifest["input_sha256"])
    if manifest["seed"] != SEED or manifest["namespace"] != ROOT.name:
        raise ValueError("campaign seed namespace changed")
    if read(ROOT / "READY.json")["campaign_sha256"] != file_hash(ROOT / "CAMPAIGN.json"):
        raise ValueError("READY does not authenticate this frozen campaign")
    pilot_recipe()
    return manifest


def original_policy():
    recipe = pilot_recipe()
    path = Path(recipe["root_adapter"])
    if recipe["root_adapter_sha256"] != ORIGINAL_SHA:
        raise ValueError("independent original root changed")
    policy = {"step": 0, "path": str(path), "adapter_sha256": ORIGINAL_SHA,
              "config_sha256": file_hash(path / "adapter_config.json"),
              "optimizer_sha256": None, "rng_sha256": None, "state_sha256": None}
    authenticate_policy(policy)
    return policy


def authenticate_policy(policy):
    path = Path(policy["path"])
    hashes = {path / "adapter_model.safetensors": policy["adapter_sha256"],
              path / "adapter_config.json": policy["config_sha256"]}
    if policy["step"]:
        hashes.update({path / "optimizer.pt": policy["optimizer_sha256"],
                       path / "rng_state.pt": policy["rng_sha256"],
                       path / "state.json": policy["state_sha256"]})
    elif policy["adapter_sha256"] != ORIGINAL_SHA:
        raise ValueError("step0 must be the independent original root")
    authenticate(hashes)


def generation_identity(campaign_id, round_id, policy, coordinate_plan_sha256):
    value = {"campaign_id": campaign_id, "round": round_id, "previous_policy": policy,
             "fixed_child_sha256": CHILD_SHA, "coordinate_plan_sha256": coordinate_plan_sha256}
    value["generation_id"] = digest(value)
    return value


def check_generation(generation, policy, optimizer_step):
    if digest({k: v for k, v in generation.items() if k != "generation_id"}) != generation["generation_id"]:
        raise ValueError("generation identity changed")
    if generation["fixed_child_sha256"] != CHILD_SHA:
        raise ValueError("fixed child changed")
    if generation["previous_policy"] != policy:
        raise ValueError("stale rollout policy or checkpoint state")
    if type(generation["round"]) is not int or not 1 <= generation["round"] <= 8:
        raise ValueError("campaign optimizer generation must be1..8")
    if generation["round"] != policy["step"] + 1 or optimizer_step != policy["step"]:
        raise ValueError("optimizer cursor must equal previous generation step")
    return generation["round"]


def contiguous_steps(steps):
    if len(set(steps)) != len(steps):
        raise ValueError("duplicate committed optimizer step")
    ordered = sorted(steps)
    if ordered != list(range(1, len(ordered) + 1)):
        raise ValueError("checkpoint commits must be contiguous")
    return len(ordered)


def reward_admission(completed, observable, strict_reward, capture_valid):
    if completed and observable and capture_valid and type(strict_reward) is int and strict_reward in (0, 1):
        return strict_reward
    return None


def checkpoint_policy(training_dir, generation, expected_input_binding=None):
    """State is the commit point, even if the process died before writing RESULT."""
    checkpoint = Path(training_dir) / f"checkpoint-{generation['round']}"
    state = read(checkpoint / "state.json")
    if state["generation"] != generation or state["optimizer_steps"] != generation["round"]:
        raise ValueError("checkpoint belongs to a stale generation or wrong optimizer cursor")
    training_dir = Path(training_dir)
    authenticate({training_dir / "INPUTS.json": state["input_file_sha256"],
                  training_dir / "correction-capture.json": state["correction_capture_sha256"]})
    saved = read(training_dir / "INPUTS.json")
    if saved != state["input_identity"]:
        raise ValueError("checkpoint saved input binding changed")
    input_binding = saved.get("input_binding", saved)
    if expected_input_binding is not None and input_binding != expected_input_binding:
        raise ValueError("checkpoint belongs to a different current input binding")
    if "group_path" in input_binding:
        group_path = Path(input_binding["group_path"])
        authenticate({group_path: input_binding["group_sha256"],
                      group_path.parent / "MANIFEST.json": input_binding["export_manifest_sha256"]})
        group = read(group_path)
        if (group["generation"] != generation or group["group_id"] != input_binding["group_id"]
                or input_binding["generation"] != generation):
            raise ValueError("checkpoint export/generation input binding changed")
    authenticate({checkpoint / name: sha for name, sha in state["files_sha256"].items()})
    required = {"adapter_model.safetensors", "adapter_config.json", "optimizer.pt", "rng_state.pt"}
    if not required <= state["files_sha256"].keys():
        raise ValueError("checkpoint missing adapter/optimizer/RNG")
    metrics = state["metrics"]
    if metrics["child_loss_tokens"] or metrics["observation_loss_tokens"] or metrics["guard_failures"]:
        raise ValueError("checkpoint violates root-only objective or distribution guards")
    if not (metrics["gradient_norm_before_clip"] > 0 and metrics["trainable_parameter_delta_l2"] > 0):
        raise ValueError("checkpoint lacks nonzero gradient/update proof")
    policy = {"step": generation["round"], "path": str(checkpoint.resolve()),
              "adapter_sha256": state["files_sha256"]["adapter_model.safetensors"],
              "config_sha256": state["files_sha256"]["adapter_config.json"],
              "optimizer_sha256": state["files_sha256"]["optimizer.pt"],
              "rng_sha256": state["files_sha256"]["rng_state.pt"],
              "state_sha256": file_hash(checkpoint / "state.json")}
    if policy["adapter_sha256"] == generation["previous_policy"]["adapter_sha256"]:
        raise ValueError("checkpoint bytes are unchanged")
    return policy
