"""Conditional checkpoint-2 policy and immutable protected-readout inputs."""
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
SPARSE = SIDE / "root-composed-rl-sparse-head-recovery-v2"
SPARSE_ATTEMPT = SPARSE / "outputs/attempt-001"
ATTEMPT = ROOT / "outputs/attempt-001"
QSR = SIDE / "root-query-sensitive-rl-v1"
QS = SIDE / "root-question-sensitive-sft-v1"
WARM = SIDE / "root-sft24-terminal-rlvr-v1"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")


def read(path):
    path = Path(path)
    try:
        relative = path.relative_to(ROOT / "inputs")
    except ValueError:
        pass
    else:
        if not path.exists():
            path = SOURCE / "inputs" / relative
    return json.loads(path.read_text())


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".pending-" + uuid.uuid4().hex)
    try:
        with temporary.open("x") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False); stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def check(path, pin):
    if sha(path) != pin:
        raise ValueError("authenticated file changed: " + str(path))


def load(name, path, pin=None):
    if pin is not None:
        check(path, pin)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def aliases(mapping):
    prior = {name: sys.modules.get(name) for name in mapping}; sys.modules.update(mapping)
    try: yield
    finally:
        for name, value in prior.items():
            if value is None: sys.modules.pop(name, None)
            else: sys.modules[name] = value


sys.path.insert(0, str(SOURCE))
import terminal_study as base  # noqa: E402

for _name in dir(base):
    if not _name.startswith("__") and _name not in globals():
        globals()[_name] = getattr(base, _name)
for _name in ("OLD", "OLD_MANIFEST", "PRIOR", "LOCAL", "CAMPAIGN", "RUNTIME", "PINS",
              "private", "prior_study", "runtime"):
    globals()[_name] = getattr(base, _name)


def data():
    return read(SOURCE / "inputs/PUBLIC.json"), read(SOURCE / "inputs/HOST_GOLD.json")


def checkpoint2_decision():
    terminal = SPARSE_ATTEMPT / "OWNER_TERMINAL.json"
    if not terminal.exists():
        return {"run": False, "reason": "sparse owner terminal absent"}
    owner = read(terminal)
    if not owner.get("complete") or not owner.get("released"):
        return {"run": False, "reason": "sparse recovery did not complete and release"}
    checkpoint = SPARSE_ATTEMPT / "training/checkpoint-2"
    state = read(checkpoint / "state.json")
    metrics = state.get("metrics") or {}
    if state.get("optimizer_steps") != 2 or tuple(metrics.get(key) for key in
            ("episodes", "root_turns", "root_action_tokens")) != (11, 154, 18517):
        raise ValueError("checkpoint2 is not the exact recovered group/update")
    required = ("adapter_model.safetensors", "adapter_config.json", "optimizer.pt", "rng_state.pt")
    for name in required:
        if state["files_sha256"].get(name) != sha(checkpoint / name):
            raise ValueError("checkpoint2 file identity: " + name)
    result = read(SPARSE_ATTEMPT / "training/RESULT.json")
    policy = result["policy"]
    if result.get("optimizer_steps") != 2 or policy != owner.get("policy"):
        raise ValueError("checkpoint2 result/owner policy mismatch")
    if (Path(policy["path"]).resolve() != checkpoint.resolve() or policy.get("step") != 2
            or policy.get("state_sha256") != sha(checkpoint / "state.json")):
        raise ValueError("checkpoint2 policy lineage mismatch")
    return {"run": True, "reason": None, "policy": policy,
            "owner_terminal_sha256": sha(terminal), "state_sha256": sha(checkpoint / "state.json")}


def verify_prepared():
    campaign = read(ROOT / "CAMPAIGN_V3.json")
    if digest({k: v for k, v in campaign.items() if k != "identity"}) != campaign["identity"]:
        raise ValueError("campaign identity")
    for path, pin in {**campaign["source_sha256"], **campaign["input_sha256"]}.items():
        check(path, pin)
    ready = read(ROOT / "READY.json")
    if ready["identity"] != campaign["identity"] or ready["campaign_sha256"] != sha(ROOT / "CAMPAIGN_V3.json"):
        raise ValueError("READY identity")
    decision = checkpoint2_decision()
    expected = {"policy": decision.get("policy"),
                "owner_terminal_sha256": decision.get("owner_terminal_sha256"),
                "state_sha256": decision.get("state_sha256")}
    if not decision["run"] or ready.get("checkpoint2") != expected:
        raise ValueError("READY checkpoint2 receipt is stale or foreign")
    return campaign


def fixed_start():
    decision = checkpoint2_decision()
    if not decision["run"]: raise ValueError(decision["reason"])
    return decision["policy"]


def endpoint_reward(reply, gold, completed, available):
    return base.endpoint_reward(reply, gold, completed, available)


def final_order(): return ("checkpoint2",)
