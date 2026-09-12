"""Keep all paired gates; additionally authenticate the V2 exact-HF reuse."""

import ast
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V1 = ROOT.parent / "helper-hf-onpolicy-other31-paired-unseen-eval-v1"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_base = load("paired_repair_eval_v1", V1 / "paired_eval_study.py")
_base.ROOT = ROOT
_base.TRAINING = ROOT.parent / "helper-hf-onpolicy-other31-paired-onestep-v2"
_base.TRAIN_READY_SHA256 = "e33c3f849abef8f05b7a09c3315980befe890ca8983b094294f1d0ce3be39807"
_base.TRAIN_READY_IDENTITY = "6b5bfc08d84a1aafd20303aa1ce6819df6ab80de1df62b6faa71dabfbb105bed"
_base.ARMS = {
    name: {
        "attempt": ROOT / f"arms/{name}/outputs/attempt-001",
        "ready": ROOT / ("READY_RLOO.json" if name == "rloo" else "READY_OTHER31.json"),
        "checkpoint": _base.TRAINING / f"outputs/attempt-001/branches/{name}/checkpoint-0001",
    }
    for name in _base.BASELINES
}
_math = load(
    "paired_repair_eval_math",
    ROOT.parent / "helper-hf-onpolicy-other31-paired-onestep-v1/pair_math.py",
)
_base.pair_math = lambda: _math
_original_plan = _base.plan


def plan(branch):
    result = _original_plan(branch)
    result["schema"] = "helper-hf-other31-paired-unseen-eval-ready-v2"
    result["collection_semantics"] = "same authenticated128 HF actions; no fresh repair sampling"
    return result


_base.plan = plan
_source = (V1 / "paired_eval_study.py").read_text()
_old_condition = 'collection.get("freshly_sampled") is not True'
assert _source.count(_old_condition) == 1
_source = _source.replace(
    _old_condition,
    '(collection.get("freshly_sampled") is not False '
    'or collection.get("reused_exact_hf_actions") is not True)',
)
_tree = ast.parse(_source)
_function = next(
    node for node in _tree.body if isinstance(node, ast.FunctionDef) and node.name == "qualify_pair"
)
exec(
    compile(
        ast.Module(body=[_function], type_ignores=[]), str(V1 / "paired_eval_study.py"), "exec"
    ),
    _base.__dict__,
)
_original_qualify = _base.qualify_pair


def verify_reuse_header(collection, proof):
    if (
        collection.get("freshly_sampled") is not False
        or collection.get("reused_exact_hf_actions") is not True
        or collection.get("fresh_model_calls_in_repair") != 0
        or collection.get("source_sampling_was_fresh") is not True
        or collection.get("source_reuse") != proof
    ):
        raise ValueError("exact unchanged-policy source reuse differs")


def qualify_pair(branch):
    result = _original_qualify(branch)
    output = _base.TRAINING / "outputs/attempt-001"
    shared = output / "shared-collection"
    proof = _base.read(_base.TRAINING / "SOURCE_PROOF.json")
    if _base.read(output / "SOURCE_REUSE.json") != proof:
        raise ValueError("source reuse proof differs")
    verify_reuse_header(_base.read(shared / "COLLECTION.json"), proof)
    source = Path(proof["source_attempt"])
    relative = ["START_RNG.pt", "AFTER_COLLECTION_RNG.pt"]
    relative += [
        f"groups/group-{index:03d}/{name}"
        for index in range(32)
        for name in ("ROLLOUT.json", "MASKS.npz", "AFTER_GROUP_RNG.pt")
    ]
    for name in relative:
        expected = proof["source_files_sha256"][str(source / "shared-collection" / name)]
        if _base.sha(shared / name) != expected:
            raise ValueError("source reuse bytes differ: " + name)
    snapshot = _base.read(output / "C32_SNAPSHOT.json")
    if snapshot["tensor_identity_sha256"] != proof["source_tensor_identity_sha256"]:
        raise ValueError("reused collection parent tensor identity differs")
    initial = {}
    for name in _base.BASELINES:
        path = output / f"branches/{name}/BRANCH_INITIAL_STATE.json"
        receipt = _base.read(path)
        if receipt != {
            "rng_identical": True,
            "rng_source_sha256": _base.sha(shared / "AFTER_COLLECTION_RNG.pt"),
            "trainable_tensor_identity_sha256": proof["source_tensor_identity_sha256"],
            "optimizer_state_empty": True,
            "learning_rate": 1e-5,
            "weight_decay": 0,
        }:
            raise ValueError("actual branch initialization differs")
        initial[name] = {"path": str(path), "sha256": _base.sha(path)}
    result.update(
        schema="helper-hf-other31-paired-eval-eligibility-v2",
        original_hf_actions_reused=128,
        fresh_repair_sampling_calls=0,
        source_collection_sha256=proof["source_collection_sha256"],
        source_reuse_sha256=_base.sha(output / "SOURCE_REUSE.json"),
        source_sampling_elapsed_seconds=proof["source_elapsed_seconds"],
        branch_initialization=initial,
    )
    return result


_base.qualify_pair = qualify_pair


def __getattr__(name):
    # CURRENT and ATTEMPT remain live selected-branch state, not copied snapshots.
    return getattr(_base, name)
