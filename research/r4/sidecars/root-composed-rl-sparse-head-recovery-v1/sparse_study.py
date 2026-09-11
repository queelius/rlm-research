"""Immutable paths and authentication for the window-03 sparse-head recovery."""
import contextlib
import hashlib
import importlib.util
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE = SIDE / "root-question-sensitive-terminal-rlvr-recovery-v2"
FAILED = SOURCE / "outputs/attempt-003/window-03"
GROUP = FAILED / "collection/export/GROUP.json"
MANIFEST = FAILED / "collection/export/MANIFEST.json"
GENERATION = FAILED / "GENERATION.json"
CHECKPOINT = SOURCE / "outputs/attempt-003/window-02/training/checkpoint-1"
ATTEMPT = ROOT / "outputs/attempt-001"
TRAIN = Path("/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python")

PINS = {
    GROUP: "7420d808187115f14ed6ca6521b77cdd1ba4ca330dd17aca92e09db430b8948f",
    MANIFEST: "bf4793681e18b12e15784194edb3a7d9966d06101fd9e5bc4db0d1f51ed96c17",
    GENERATION: "bff4dc8e048496f35f2a7aaa14bf29c4c51f8362dca5f0d5f39040669be41cee",
    CHECKPOINT / "adapter_model.safetensors": "358d2cefa3fe49f0f5201b0ddf7b4d55e63db9249be4e10b0dec17faa8c24244",
    CHECKPOINT / "adapter_config.json": "ac73679bf97e7f812e39a518306cbe7c39829b0c4f8d9af4a0c9871985a5e80a",
    CHECKPOINT / "optimizer.pt": "f37d02fd4137ed59706f9d7b017604dd7c608d905ecc6b6e222293e13980f27b",
    CHECKPOINT / "rng_state.pt": "855616cdeabe51ae463c56026606115a6a8082032870c55d611f4ca6b2442f7f",
    CHECKPOINT / "state.json": "93300fe9cd8cb342f8a9aec8fbee833fd7da0a2caa97529ec44a177b73264c66",
    SOURCE / "RECIPE.json": "3c26d09a83f21357d0825e019bf29302b1e1954f769dbceb4359aede527d8b67",
    SOURCE / "CAMPAIGN.json": "eaa351d213d1128464429cd47aede0e32ebac283958ce4d8abb9ed78353e167d",
    SIDE / "root-rlvr-campaign-v1/campaign_train.py": "38fe3087b8deb94ee8e0fa2e0330ca34a822f84192031c389ff32acf00d79d1f",
    SIDE / "single-gpu-rlvr-v2/source/single_gpu_rlvr_tis_v3.py": "eff526cf496d3896e220d5aa0694bed3b703114e4a19d6f7c9e4f73de6240bd9",
}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def check(path, pin):
    if sha(path) != pin:
        raise ValueError("authenticated file changed: " + str(path))


def write(path, value):
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


@contextlib.contextmanager
def aliases(mapping):
    old = {name: sys.modules.get(name) for name in mapping}
    sys.modules.update(mapping)
    try:
        yield
    finally:
        for name, value in old.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


def verify_inputs():
    for path, pin in PINS.items():
        check(path, pin)
    group, generation, manifest = read(GROUP), read(GENERATION), read(MANIFEST)
    if group["generation"] != generation or manifest["generation"] != generation:
        raise ValueError("frozen group/generation mismatch")
    if generation["round"] != 2 or generation["previous_policy"]["step"] != 1:
        raise ValueError("not exact failed update2 lineage")
    if generation["previous_policy"]["path"] != str(CHECKPOINT):
        raise ValueError("previous checkpoint path changed")
    state = read(CHECKPOINT / "state.json")
    if state["optimizer_steps"] != 1:
        raise ValueError("checkpoint is not Adam1")
    turns = [turn for episode in group["episodes"] for turn in episode["turns"]]
    lengths = [len(turn["input_ids"]) for turn in turns]
    actions = [len(turn["old_logprobs"]) for turn in turns]
    receipt = {
        "previous_optimizer_step": 1,
        "target_optimizer_step": 2,
        "episodes": len(group["episodes"]),
        "turns": len(turns),
        "causal_tokens": sum(lengths),
        "action_tokens": sum(actions),
        "max_sequence_tokens": max(lengths),
        "max_action_tokens": max(actions),
        "group_sha256": PINS[GROUP],
        "generation_sha256": PINS[GENERATION],
        "checkpoint1_state_sha256": PINS[CHECKPOINT / "state.json"],
    }
    if tuple(receipt[k] for k in ("episodes", "turns", "causal_tokens", "action_tokens", "max_sequence_tokens", "max_action_tokens")) != (11, 154, 647114, 18517, 8192, 219):
        raise ValueError("frozen workload inventory changed")
    return receipt


def verify_prepared():
    campaign = read(ROOT / "CAMPAIGN.json")
    if digest({key: value for key, value in campaign.items() if key != "identity"}) != campaign["identity"]:
        raise ValueError("campaign identity changed")
    for path, pin in {**campaign["source_sha256"], **campaign["input_sha256"]}.items():
        check(path, pin)
    if campaign["frozen_inventory"] != verify_inputs():
        raise ValueError("campaign inventory changed")
    ready = read(ROOT / "READY.json")
    if ready["identity"] != campaign["identity"] or ready["campaign_sha256"] != sha(ROOT / "CAMPAIGN.json"):
        raise ValueError("READY does not bind campaign")
    return campaign
