"""One small inference-only factorial; original collectors and datasets are read-only."""

import copy
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent / "root-rlvr-campaign-v1"
CONTINUATION = ROOT.parent / "root-recovered-child-continuation-v1"
PRIOR_RUN = CONTINUATION / "outputs/attempt-001"
sys.path.insert(0, str(CAMPAIGN))
import campaign_common as c
import campaign_native as native
sys.path.insert(0, str(ROOT))

BASE_BINDING = native.binding_for
ARMS = ("unchanged", "contract")
WEIGHTS = ("original", "step8")
SEED_MASTER = 981261900
ORDER_MASTER = 981261901
STEP8_SHA = "473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd"
SUFFIX = ("\n\nReturn-type contract: The .answer field returned by rlm(...) is text, "
          "not a Python list. If it contains a JSON array, decode it with json.loads "
          "before treating it as a list.")


def policies():
    original = c.original_policy()
    commit = c.read(PRIOR_RUN / "round-08/COMMIT.json")
    step8 = c.checkpoint_policy(PRIOR_RUN / "round-08/training", commit["generation"])
    if (step8 != commit["policy"] or step8["step"] != 8
            or step8["adapter_sha256"] != STEP8_SHA):
        raise ValueError("not the exact final step8 policy requested by the coordinator")
    return {"original": original, "step8": step8}


def weight_for(policy):
    for weight, expected in policies().items():
        if policy == expected:
            return weight
    raise ValueError("policy is not one of the two frozen root identities")


def binding_for(policy):
    weight = weight_for(policy)
    return {**BASE_BINDING(policy), "return_contract_study": ROOT.name,
            "return_contract_weight": weight, "design_sha256": c.file_hash(ROOT / "DESIGN.md")}


def validate_binding(binding):
    weight = weight_for(binding["campaign_policy"])
    native.authenticate_binding(binding)
    if binding != binding_for(binding["campaign_policy"]):
        raise ValueError("factorial binding differs from exact root/fixed-child/design identity")
    return weight


def planned_endpoint(binding):
    return {"url": "http://127.0.0.1:18601/v1", "model": binding["role_map"]["root"],
            "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY",
            "renderer_model": c.pilot_recipe()["base_model"]}


def make_tasks():
    tasks = native.make_tasks()
    names = {r["task_name"] for r in native.planned_rows("transfer-original")}
    tasks = {name: tasks[name] for name in sorted(names)}
    expected = c.read(CAMPAIGN / "inputs/TASK_IDENTITIES.json")
    if native.task_identity(tasks) != {name: expected[name] for name in tasks}:
        raise ValueError("original transfer task/prompt/context bytes changed")
    if len(tasks) != 12 or len({t.data.context_window_id for t in tasks.values()}) != 6:
        raise ValueError("expected exactly 12 tasks and six exposed source contexts")
    return tasks


def with_prompt(task, arm):
    if arm not in ARMS:
        raise ValueError("unknown return-type instruction")
    baseline = native.capture.role.with_prompt(task, "sft_child")
    if arm == "unchanged":
        return baseline
    return type(task)(baseline.data.model_copy(update={"prompt": baseline.data.prompt + SUFFIX}),
                      task.config)


def prior_seeds():
    result = set()
    def visit(value):
        if isinstance(value, dict):
            if type(value.get("seed")) is int:
                result.add(value["seed"])
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    for path in (CAMPAIGN / "inputs/PLANS.json", c.PILOT / "inputs/PLAN.json",
                 ROOT.parent / "root-credit-validation-replay-v1/SPEC_ORIGINAL.json"):
        visit(c.read(path))
    return result


def phase_order():
    return sorted(WEIGHTS, key=lambda w: c.digest([ROOT.name, ORDER_MASTER, "weight-order", w]))


def build_plan(tasks):
    old = {(r["task_name"], r["repeat"]): r for r in native.planned_rows("transfer-original")}
    pairs = []
    for index, ((name, repeat), prior) in enumerate(sorted(old.items())):
        seed = int(c.digest([ROOT.name, SEED_MASTER, name, repeat])[:8], 16) % (2**31 - 1)
        identity = {"study": ROOT.name, "task_name": name, "source_id": prior["source_id"],
            "context_window_id": prior["context_window_id"], "context_sha256": prior["context_sha256"],
            "analysis_split": "exposed_root_transfer_leaf_train_supported",
            "split": "transfer", "repeat": repeat, "seed": seed, "temperature": .5,
            "client_path": "train"}
        identity["matched_id"] = c.digest(identity)
        order = ARMS if index % 2 == 0 else tuple(reversed(ARMS))
        pairs.append((identity, order))
    pairs.sort(key=lambda p: c.digest([ROOT.name, ORDER_MASTER, "pair-order", p[0]["matched_id"]]))
    plan = []
    for phase, weight in enumerate(phase_order()):
        for identity, order in pairs:
            for position, arm in enumerate(order):
                row = {**identity, "weight": weight, "arm": arm, "phase_index": phase,
                    "pair_id": c.digest([identity["matched_id"], weight]), "pair_order": position,
                    "group_id": c.digest([ROOT.name, identity["task_name"], weight, arm]),
                    "task_hash": with_prompt(tasks[identity["task_name"]], arm).hash,
                    "prior_coordinate_id": old[(identity["task_name"], identity["repeat"])]["id"],
                    "dispatch_order": len(plan)}
                row["id"] = c.digest(row)
                plan.append(row)
    if len({r["seed"] for r in plan}) != 24 or {r["seed"] for r in plan} & prior_seeds():
        raise ValueError("new seeds collide with one another or checked prior root plans")
    return plan


def task_identities(tasks):
    identities = []
    for name, task in tasks.items():
        arms = {arm: {"prompt": with_prompt(task, arm).data.prompt,
                      "prompt_sha256": hashlib.sha256(with_prompt(task, arm).data.prompt.encode()).hexdigest(),
                      "task_hash": with_prompt(task, arm).hash} for arm in ARMS}
        identities.append({"name": name, "hash": task.hash,
            "context_sha256": hashlib.sha256(task.data.context.encode()).hexdigest(),
            "context_window_id": task.data.context_window_id, "arms": arms,
            "intended_hash_differences": ["contract prompt SHA", "contract task hash"],
            "unchanged": ["original task", "context", "gold", "task config", "system/harness environment"]})
    return identities


def prepare():
    campaign = c.verify_campaign()
    tasks, bound_policies = make_tasks(), policies()
    plan = build_plan(tasks)
    bindings = {weight: binding_for(policy) for weight, policy in bound_policies.items()}
    c.write_once(ROOT / "inputs/PLAN.json", plan)
    c.write_once(ROOT / "inputs/TASKS.json", task_identities(tasks))
    c.write_once(ROOT / "inputs/POLICIES.json", bound_policies)
    for weight, binding in bindings.items():
        c.write_once(ROOT / f"inputs/BINDING-{weight}.json", binding)
    base = c.read(PRIOR_RUN / "transfer-original/CAPTURE_SPEC.json")
    if base["environment"] != c.read(c.PILOT / "SPEC.json")["environment"]:
        raise ValueError("prior native transfer environment differs from qualified pilot")
    sources = {**base["source_file_sha256"], **campaign["source_sha256"], **campaign["input_sha256"]}
    paths = [ROOT / n for n in ("study.py", "driver.py", "analysis.py", "qualify.py", "test_study.py", "DESIGN.md", "PLAN.md", "RUNBOOK.md")]
    paths += list((ROOT / "inputs").glob("*.json"))
    paths += [PRIOR_RUN / "round-08/COMMIT.json", PRIOR_RUN / "round-08/GENERATION.json",
              PRIOR_RUN / "transfer-original/CAPTURE_SPEC.json", CAMPAIGN / "LIFECYCLE_V2.json", CAMPAIGN / "READY_V2.json",
              CAMPAIGN / "campaign_lifecycle_v2.py", CONTINUATION / "AMENDMENT.json"]
    for policy in bound_policies.values():
        paths += [Path(policy["path"]) / n for n in ("adapter_model.safetensors", "adapter_config.json")]
        if policy["step"]:
            paths.append(Path(policy["path"]) / "state.json")
    sources.update({str(p): c.file_hash(p) for p in paths})
    c.authenticate(sources)
    spec = {"schema": ROOT.name, "source_file_sha256": sources,
        "plan": plan, "plan_sha256": c.digest(plan), "tasks": task_identities(tasks),
        "environment": base["environment"], "image_id": base["image_id"],
        "policies": bound_policies, "bindings": bindings, "instruction_suffix": SUFFIX,
        "phase_order": phase_order(), "seed_master": SEED_MASTER, "order_master": ORDER_MASTER,
        "seed_audit": {"prior_root_plan_seed_count": len(prior_seeds()), "collisions": 0,
            "scope": "campaign train/validation/transfer, pilot and unchanged validation replay; no exhaustive global seed registry claim"},
        "max_concurrent_pairs": 8, "wall_time_cap_seconds": 3600, "cleanup_reserve_seconds": 90,
        "phase_collection_cap_seconds": 1800, "service_ready_cap_seconds": 180,
        "sampling": {"temperature": .5, "top_p": 1, "top_k": -1, "min_p": 0, "max_tokens": 2048},
        "renderer": {"name": "qwen3", "enable_thinking": True},
        "base_model": c.pilot_recipe()["base_model"], "base_manifest_sha256": c.pilot_recipe()["base_manifest_sha256"],
        "source_provenance": c.read(CAMPAIGN / "inputs/PROVENANCE.json"),
        "exposure": "same 12 tasks/24 matched coordinates already read out; six formerly root-new, fixed-child source-train-supported contexts; fresh seeds only",
        "objective": "inference only; unchanged strict task scorer; no rewards used for training",
        "primary_unit": "task/seed matched contrasts with six context-group summaries",
        "order_nuisance": "two root-weight phases; instruction pairs balanced within each; root weight confounded with service/time/order",
        "inherited_retry_caveat": "outer max_retries=0 does not remove nano internal call_with_retries delays; all physical attempts/wall time retained",
        "partial_trace_limitation": base["partial_trace_limitation"]}
    c.write_once(ROOT / "SPEC.json", spec)
    return spec


def verify():
    spec = c.read(ROOT / "SPEC.json")
    c.authenticate(spec["source_file_sha256"])
    c.verify_campaign()
    tasks = make_tasks()
    if (spec["plan"] != build_plan(tasks) or spec["plan_sha256"] != c.digest(spec["plan"])
            or spec["tasks"] != task_identities(tasks) or spec["policies"] != policies()
            or spec["instruction_suffix"] != SUFFIX or spec["phase_order"] != phase_order()
            or spec["environment"] != c.read(c.PILOT / "SPEC.json")["environment"]):
        raise ValueError("frozen task/plan/policy/environment identity changed")
    for weight, binding in spec["bindings"].items():
        if validate_binding(binding) != weight:
            raise ValueError("root weight label differs from actual binding")
    return spec


def validate_descriptor(descriptor, binding, binding_path):
    validate_binding(binding)
    root = binding["models"][binding["role_map"]["root"]]
    if (descriptor["model_alias"] != binding["role_map"]["root"]
            or descriptor["adapter"] != {"path": root["path"], "model_sha256": root["adapter_sha256"], "config_sha256": root["config_sha256"]}
            or descriptor["role_binding_sha256"] != c.file_hash(binding_path)
            or descriptor["base_model"]["manifest_sha256"] != c.pilot_recipe()["base_manifest_sha256"]
            or descriptor["base_model"]["path"] != c.pilot_recipe()["base_model"]):
        raise ValueError("actual endpoint does not authenticate exact root/base/config/binding")
    endpoint = planned_endpoint(binding)
    endpoint["url"] = f"http://{descriptor['host']}:{descriptor['port']}/v1"
    endpoint["api_key_env"] = descriptor["api_key_env"]
    return endpoint


def phase_spec(weight, binding_path, endpoint_path, destination, cap):
    spec = copy.deepcopy(verify())
    binding, descriptor = c.read(binding_path), c.read(endpoint_path)
    if binding != spec["bindings"][weight]:
        raise ValueError("actual service bound a different study/weight")
    endpoint = validate_descriptor(descriptor, binding, binding_path)
    spec.update(endpoint=endpoint, role_binding=binding, weight=weight,
        binding_path=str(Path(binding_path).resolve()), endpoint_descriptor_path=str(Path(endpoint_path).resolve()),
        source_endpoint_descriptor=descriptor, plan=[r for r in spec["plan"] if r["weight"] == weight],
        wall_time_cap_seconds=min(float(cap), spec["phase_collection_cap_seconds"]),
        serving_evidence=native.capture.recursive.serving_evidence(Path(endpoint_path).parent / "inference.log"),
        parent_spec_sha256=c.file_hash(ROOT / "SPEC.json"))
    spec["plan_sha256"] = c.digest(spec["plan"])
    spec["source_file_sha256"].update({str(p): c.file_hash(p) for p in (Path(binding_path), Path(endpoint_path), ROOT / "SPEC.json", ROOT / "READY.json")})
    c.write_once(destination, spec)
    return spec


def verify_phase(path):
    parent, actual = verify(), c.read(path)
    c.authenticate(actual["source_file_sha256"])
    weight = actual["weight"]
    expected = [r for r in parent["plan"] if r["weight"] == weight]
    if (actual["parent_spec_sha256"] != c.file_hash(ROOT / "SPEC.json") or actual["plan"] != expected
            or actual["plan_sha256"] != c.digest(expected) or actual["tasks"] != parent["tasks"]
            or actual["environment"] != parent["environment"] or actual["image_id"] != parent["image_id"]
            or actual["max_concurrent_pairs"] != 8 or not 0 < actual["wall_time_cap_seconds"] <= 1800
            or any(actual["source_file_sha256"].get(p) != sha for p, sha in parent["source_file_sha256"].items())):
        raise ValueError("phase changed frozen coordinates/tasks/runtime/sources")
    binding, descriptor = c.read(actual["binding_path"]), c.read(actual["endpoint_descriptor_path"])
    if (binding != parent["bindings"][weight] or actual["role_binding"] != binding
            or actual["source_endpoint_descriptor"] != descriptor
            or actual["endpoint"] != validate_descriptor(descriptor, binding, actual["binding_path"])):
        raise ValueError("phase actual endpoint binding changed")
    native.capture.recursive.validate_serving_evidence(actual["serving_evidence"])
    return actual
