"""Additive result-authenticated post-root-update binding and exact validation replay."""

import argparse
import asyncio
import copy
import json
import math
from pathlib import Path

import replay

ROOT, PHASE1, phase1 = replay.ROOT, replay.PHASE1, replay.phase1
POST_ALIAS = "strict-rlm-qwen3-4b-root-tis-step1-v1"
RECIPE = PHASE1 / "TRAINING_RECIPE.json"
RECIPE_SHA = "f1c226b08de69f29250efc69cc0634fd17db1ffd88c0f1ef0ab2edb8a91bdb96"
TRAINER = PHASE1 / "source/train_root.py"


def validate_result_contract(result, *, original_root_sha, child_sha, recipe_sha):
    if (result.get("schema") != "one-step-root-only-tis-result-v1"
            or result.get("optimizer_steps") != 1 or result.get("child_loss_tokens") != 0
            or result.get("observation_loss_tokens") != 0 or result.get("recipe_sha256") != recipe_sha
            or result.get("correction_diagnostics", {}).get("guard_failures") != []):
        raise ValueError("successful declared one-step root-only result required")
    for key in ("gradient_norm_before_clip", "trainable_parameter_delta_l2"):
        value = result.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError("finite nonzero root gradient and parameter delta required")
    execution = result["input_identity"]
    inputs = execution["input_binding"]
    if (inputs["original_root_sha256"] != original_root_sha or inputs["fixed_child_sha256"] != child_sha
            or execution.get("child_adapter_loaded_into_training_model") is not False):
        raise ValueError("starting-root/fixed-child training identity differs")


def authenticate_result(result_path):
    source = replay.ORIGINAL_VERIFY()
    if phase1.file_hash(PHASE1 / "SPEC.json") != replay.PHASE1_SPEC_SHA or phase1.file_hash(RECIPE) != RECIPE_SHA:
        raise ValueError("declared Phase1/training recipe identity changed")
    result = phase1.read(result_path)
    bound = source["role_binding"]
    original_root = bound["models"][bound["role_map"]["root"]]["adapter_sha256"]
    child = bound["models"][bound["fixed_child"]]["adapter_sha256"]
    validate_result_contract(result, original_root_sha=original_root, child_sha=child, recipe_sha=RECIPE_SHA)
    checkpoint = Path(result["checkpoint"]).resolve()
    if checkpoint != result_path.parent / "checkpoint-1":
        raise ValueError("result checkpoint must be its own checkpoint-1")
    state_path = checkpoint / "state.json"
    if phase1.file_hash(state_path) != result["checkpoint_state_sha256"]:
        raise ValueError("checkpoint state hash mismatch")
    state = phase1.read(state_path)
    execution = result["input_identity"]
    inputs = execution["input_binding"]
    if (state["input_identity"] != execution or state["cursor"]["optimizer_steps"] != 1
            or execution["execution_identity"] != phase1.digest({k: v for k, v in execution.items() if k != "execution_identity"})
            or inputs["input_identity"] != phase1.digest({k: v for k, v in inputs.items() if k != "input_identity"})
            or inputs["role_binding"] != bound):
        raise ValueError("checkpoint/training input envelope mismatch")
    hashes = {str(result_path): phase1.file_hash(result_path), str(state_path): result["checkpoint_state_sha256"],
              str(RECIPE): RECIPE_SHA, **inputs["source_sha256"],
              inputs["group_path"]: inputs["group_sha256"],
              str(Path(inputs["group_path"]).parent / "MANIFEST.json"): inputs["export_manifest_sha256"],
              str(result_path.parent / "correction-capture.json"): result["correction_capture_sha256"]}
    if str(TRAINER) not in hashes:
        raise ValueError("result does not bind the declared root-only trainer source")
    for name, expected in state["files_sha256"].items():
        if Path(name).name != name:
            raise ValueError("invalid checkpoint manifest path")
        hashes[str(checkpoint / name)] = expected
    for path, expected in hashes.items():
        if phase1.file_hash(path) != expected:
            raise ValueError(f"post-update provenance hash mismatch: {path}")
    if (state["files_sha256"]["adapter_model.safetensors"] != result["new_adapter_sha256"]
            or result["new_adapter_sha256"] == original_root):
        raise ValueError("actual changed root adapter identity missing")
    return source, result, state, hashes


def post_binding(source, result, state, result_path):
    old = source["role_binding"]
    child_alias = old["fixed_child"]
    return {"schema": "root-credit-postupdate-role-binding-v1",
        "selection_path": old["selection_path"], "selection_sha256": old["selection_sha256"],
        "selected_epoch": old["selected_epoch"], "role_map": {"root": POST_ALIAS, "children": [child_alias]},
        "models": {POST_ALIAS: {"path": result["checkpoint"], "adapter_sha256": result["new_adapter_sha256"],
                                 "config_sha256": state["files_sha256"]["adapter_config.json"]},
                   child_alias: copy.deepcopy(old["models"][child_alias])},
        "root_training_result": str(result_path), "root_training_result_sha256": phase1.file_hash(result_path),
        "root_training_checkpoint_state_sha256": result["checkpoint_state_sha256"],
        "root_training_recipe_sha256": RECIPE_SHA, "source_phase1_spec_sha256": replay.PHASE1_SPEC_SHA,
        "post_training_test_consulted_for_binding": False}


def validate_endpoint(source, endpoint, binding, binding_sha):
    root = binding["models"][POST_ALIAS]
    expected = {"path": root["path"], "model_sha256": root["adapter_sha256"], "config_sha256": root["config_sha256"]}
    if (endpoint.get("host") != "127.0.0.1" or not 0 < int(endpoint["port"]) < 65536
            or endpoint.get("model_alias") != POST_ALIAS or endpoint.get("adapter") != expected
            or endpoint.get("base_model") != source["source_endpoint_descriptor"]["base_model"]
            or endpoint.get("role_binding_sha256") != binding_sha):
        raise ValueError("actual post-update root alias/adapter/base/binding mismatch")


def prepare(result_path, binding_path, endpoint_path, server_log, spec_path):
    source, result, state, hashes = authenticate_result(result_path)
    binding = phase1.read(binding_path)
    if binding != post_binding(source, result, state, result_path):
        raise ValueError("supplied role binding differs from authenticated trainer result")
    endpoint = phase1.read(endpoint_path)
    validate_endpoint(source, endpoint, binding, phase1.file_hash(binding_path))
    if Path(endpoint["prime_inference_config"]).resolve().parent != server_log.parent:
        raise ValueError("current serving log does not belong to supplied endpoint service")
    plan, tasks = replay.validation_subset(source)
    spec = copy.deepcopy(source)
    actual = {"url": f"http://{endpoint['host']}:{endpoint['port']}/v1", "model": POST_ALIAS,
              "api_key_env": endpoint["api_key_env"], "renderer_model": endpoint["base_model"]["path"]}
    spec.update(schema=ROOT.name + "-postupdate", endpoint=actual, source_endpoint_descriptor=endpoint,
        plan=plan, tasks=tasks, plan_sha256=phase1.digest(plan), coordinate_plan_sha256=phase1.digest(plan),
        role_binding={**binding, "fixed_child": source["role_binding"]["fixed_child"]},
        role_binding_file_sha256=phase1.file_hash(binding_path), binding_sha256=phase1.digest(binding),
        serving_evidence=phase1.recursive.serving_evidence(server_log),
        request_template=phase1.native.request_metadata(actual, plan[0]),
        replay_condition="one_step_root_tis_with_unchanged_selected_child",
        interpretation="Exact validation8 after one root-only update; compare with original replay variability, not seed-based determinism assumptions.",
        training_policy="Validation only; no optimizer, training-group export or outcome-based task selection.",
        post_binding_inputs={"result_path": str(result_path), "binding_path": str(binding_path), "endpoint_path": str(endpoint_path)},
        phase1_spec_sha256=replay.PHASE1_SPEC_SHA)
    paths = (Path(__file__), ROOT / "test_post_binding.py", ROOT / "replay.py", ROOT / "SPEC_ORIGINAL.json", binding_path, endpoint_path)
    hashes.update({str(path): phase1.file_hash(path) for path in paths})
    spec["source_file_sha256"].update(hashes)
    phase1.write_once(spec_path, spec)
    spec_path.chmod(0o444)
    return spec


def verify(spec_path, result_path, binding_path, endpoint_path):
    source, result, state, hashes = authenticate_result(result_path)
    spec = phase1.read(spec_path)
    for path, expected in {**spec["source_file_sha256"], **hashes}.items():
        if phase1.file_hash(path) != expected:
            raise ValueError(f"post-replay source changed: {path}")
    binding = phase1.read(binding_path)
    if binding != post_binding(source, result, state, result_path):
        raise ValueError("bound checkpoint/result changed")
    endpoint = phase1.read(endpoint_path)
    validate_endpoint(source, endpoint, binding, phase1.file_hash(binding_path))
    if spec["source_endpoint_descriptor"] != endpoint or spec["role_binding"] != {**binding, "fixed_child": source["role_binding"]["fixed_child"]}:
        raise ValueError("post spec differs from explicit runtime binding")
    plan, tasks = replay.validation_subset(source)
    if spec["plan"] != plan or spec["tasks"] != tasks or spec["plan_sha256"] != phase1.digest(plan):
        raise ValueError("post-update validation tasks/coordinates changed")
    phase1.recursive.validate_serving_evidence(spec["serving_evidence"])
    return spec


async def run(spec_path, result_path, binding_path, endpoint_path, output):
    spec = verify(spec_path, result_path, binding_path, endpoint_path)
    names = {row["task_name"] for row in spec["plan"]}
    tasks = {name: task for name, task in replay.ORIGINAL_TASKS().items() if name in names}
    for row in spec["plan"]:
        if phase1.role.with_prompt(tasks[row["task_name"]], "sft_child").hash != row["task_hash"]:
            raise ValueError("post-update runtime prompt hash changed")
    old_verify, old_tasks = phase1.verify, phase1.make_tasks
    try:
        phase1.verify, phase1.make_tasks = lambda: copy.deepcopy(spec), lambda: tasks
        return await phase1.run(output)
    finally:
        phase1.verify, phase1.make_tasks = old_verify, old_tasks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("bind", "prepare", "verify", "run"))
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--binding", type=Path, default=ROOT / "POST_BOUND_WEIGHTS.json")
    parser.add_argument("--endpoint", type=Path)
    parser.add_argument("--server-log", type=Path)
    parser.add_argument("--spec", type=Path, default=ROOT / "SPEC_POST_UPDATE.json")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/postupdate-replay-attempt-001")
    args = parser.parse_args()
    result, binding = args.result.resolve(), args.binding.resolve()
    if args.command == "bind":
        source, record, state, _ = authenticate_result(result)
        value = post_binding(source, record, state, result)
        phase1.write_once(binding, value)
        print(json.dumps({"binding_sha256": phase1.file_hash(binding), "root_alias": POST_ALIAS, "gpu_calls": 0}))
        return
    if args.endpoint is None or (args.command == "prepare" and args.server_log is None):
        parser.error("explicit assigned endpoint required; prepare also needs its current server log")
    endpoint, spec = args.endpoint.resolve(), args.spec.resolve()
    if args.command == "run":
        raise SystemExit(asyncio.run(run(spec, result, binding, endpoint, args.output.resolve())))
    value = prepare(result, binding, endpoint, args.server_log.resolve(), spec) if args.command == "prepare" else verify(spec, result, binding, endpoint)
    print(json.dumps({"planned": len(value["plan"]), "root_alias": POST_ALIAS, "spec_sha256": phase1.file_hash(spec), "gpu_calls": 0}))


if __name__ == "__main__":
    main()
