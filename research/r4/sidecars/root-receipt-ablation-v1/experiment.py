"""Private adapters over the frozen native root collector; no source hot patches."""
import copy
import hashlib
import importlib.util
import itertools
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / "root-return-contract-factorial-v1"
DECISION = ROOT.parents[1] / "operations/2026-09-09-continuous-allocation/RECEIPT_IMPLEMENTATION_DECISION.md"
ARMS = ("unchanged", "indexed_raw", "receipt")
SEED_MASTER = 981267100


def private(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


old = private("receipt_original_study", PRIOR / "study.py")
c, native = old.c, old.native
capture = native.capture
sys.path.insert(0, str(ROOT))
from receipt_api import build_request
from oolong_prime_rlm_strict_v1.taskset import StrictOolongTask

COLLECTOR = Path(capture.base.__file__)
COLLECTOR_SHA = "406a64ca59e4d77e6126c3fd97339c57cb5d7aef6808c998d7e18be7e6456832"


def collector_source():
    if c.file_hash(COLLECTOR) != COLLECTOR_SHA:
        raise ValueError("inherited native collector changed")
    source = COLLECTOR.read_text()
    for before, after in (("range(0, len(plan), 2)", "range(0, len(plan), 3)"),
                          ("plan[offset : offset + 2]", "plan[offset : offset + 3]")):
        if source.count(before) != 1:
            raise ValueError("expected exactly one original pair-grouping seam")
        source = source.replace(before, after)
    return source


def collector():
    # Preserve every inherited global/dependency; only run's queue chunks differ.
    module = types.ModuleType("receipt_triple_collector")
    module.__dict__.update(capture.base.__dict__)
    code = compile(collector_source(), str(COLLECTOR), "exec")
    # Executing only the run function avoids inherited module initialization.
    import ast
    tree = ast.parse(collector_source())
    node = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "run")
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(COLLECTOR), "exec"), module.__dict__)
    return module


def make_tasks():
    return old.make_tasks()


def catalog_for(task):
    public = c.read(c.ROOT / "inputs/TRANSFER_PUBLIC.json")
    context = next(row for row in public["contexts"] if row["sha256"] == hashlib.sha256(task.data.context.encode()).hexdigest())
    lines = context["text"].splitlines(keepends=True)
    if len(lines) != 64 or len(context["group_ids"]) != 64 or any(" || Instance: " not in line for line in lines):
        raise ValueError("public context record boundaries changed")
    return {"context_sha256": context["sha256"], "context_id": context["id"],
        "records": [{"id": f"q{index+1:04d}", "text": line,
            "text_sha256": hashlib.sha256(line.encode()).hexdigest(), "group_id": group}
            for index, (line, group) in enumerate(zip(lines, context["group_ids"], strict=True))]}


class ReceiptTask(StrictOolongTask):
    async def setup(self, trace, runtime):
        await super().setup(trace, runtime)
        await runtime.write("receipt_api.py", (ROOT / "receipt_api.py").read_bytes())
        await runtime.write("receipt_catalog.json", json.dumps(catalog_for(self), sort_keys=True).encode())
        await runtime.write("receipt_config.json", json.dumps({"arm": self.receipt_arm}).encode())

    async def finalize(self, trace, runtime):
        await super().finalize(trace, runtime)
        try:
            payload = await runtime.read("receipt_audit.jsonl", max_bytes=8 * 1024 * 1024)
            trace.info["receipt_audit"] = {"raw": payload.decode(), "sha256": hashlib.sha256(payload).hexdigest(),
                "trust": "root-writable diagnostics; corroborate native calls"}
        except Exception as error:
            # Missing or unavailable diagnostic files do not change the task score.
            trace.info["receipt_audit"] = {"raw": None, "error_type": type(error).__name__, "message": str(error)}


def with_prompt(task, arm):
    if arm not in ARMS:
        raise ValueError("unknown arm")
    baseline = old.with_prompt(task, "unchanged")
    if arm == "unchanged":
        return baseline
    before = "Executable API example for the first four context records"
    after = "\n\nQuestion: "
    prompt = baseline.data.prompt
    if prompt.count(before) != 1 or prompt.count(after) != 1:
        raise ValueError("historical example boundary changed")
    prefix = prompt.split(before)[0]
    # Remove only the compulsory-sounding full-label suggestion equally in new arms.
    prefix = prefix.split("Suggested procedure:")[0]
    example = ("Optional source-bound helper: you may select any source records, query, result vocabulary, "
        "batching and recovery, or continue using ordinary rlm(prompt). No complete label vector is required. "
        "source_records() returns public id/text records. rlm_records(ids, query, allowed_values) returns "
        "the unmodified child answer text and native session/usage/turn metadata.\n"
        "```python\nfrom receipt_api import source_records, rlm_records\n"
        "records = source_records()\nids = [r['id'] for r in records[:4]]\n"
        "child = await rlm_records(ids, 'Does the question ask for a human being, organization or group of people? '"
        "'Use yes for a match and no otherwise.', ['yes', 'no'])\n")
    if arm == "receipt":
        example += ("receipt = child.receipt()\nprint(receipt)\n```\n"
            "The optional receipt reports missing, duplicate, unknown IDs and invalid labels or JSON. "
            "labels_by_id is available only when valid is true; validity does not establish semantic correctness. "
            "Raw text is still child.answer. You decide whether/how to recover and answer the task.")
    else:
        example += ("print(child.answer)\n```\n"
            "You may decode the raw JSON with Python and inspect it. You decide whether/how to recover "
            "and answer the task.")
    result = ReceiptTask(baseline.data.model_copy(update={"prompt": prefix + example + after + prompt.split(after)[1]}), task.config)
    result.receipt_arm = arm
    return result


def build_plan(tasks):
    old_rows = {(r["task_name"], r["repeat"]): r for r in native.planned_rows("transfer-original")}
    orders = list(itertools.permutations(ARMS))
    triples = []
    for index, ((name, repeat), prior) in enumerate(sorted(old_rows.items())):
        identity = {"study": ROOT.name, "task_name": name, "source_id": prior["source_id"],
            "context_window_id": prior["context_window_id"], "context_sha256": prior["context_sha256"],
            "analysis_split": "exposed_root_transfer_leaf_train_supported", "split": "transfer",
            "repeat": repeat, "seed": SEED_MASTER + 1 + index, "temperature": .5, "client_path": "train"}
        identity["matched_id"] = c.digest(identity)
        triples.append((identity, orders[index % 6]))
    triples.sort(key=lambda item: c.digest([SEED_MASTER, "triple-order", item[0]["matched_id"]]))
    plan = []
    for identity, order in triples:
        for position, arm in enumerate(order):
            row = {**identity, "weight": "step8", "arm": arm, "phase_index": 0,
                "pair_id": identity["matched_id"], "pair_order": position,
                "group_id": c.digest([ROOT.name, identity["task_name"], arm]),
                "task_hash": with_prompt(tasks[identity["task_name"]], arm).hash,
                "dispatch_order": len(plan)}
            row["id"] = c.digest(row)
            plan.append(row)
    return plan


def binding_for(policy):
    frozen = c.read(PRIOR / "SPEC.json")
    if policy != frozen["policies"]["step8"]:
        raise ValueError("only historical step8 root is permitted")
    bound = copy.deepcopy(frozen["bindings"]["step8"])
    for key in ("return_contract_study", "return_contract_weight", "design_sha256"):
        bound.pop(key, None)
    return {**bound, "receipt_study": ROOT.name, "decision_sha256": c.file_hash(DECISION)}


def validate_descriptor(descriptor, binding, binding_path):
    native.authenticate_binding(binding)
    if binding != binding_for(binding["campaign_policy"]):
        raise ValueError("binding differs from frozen receipt identity")
    root = binding["models"][binding["role_map"]["root"]]
    if (descriptor["model_alias"] != binding["role_map"]["root"]
            or descriptor["adapter"] != {"path": root["path"], "model_sha256": root["adapter_sha256"], "config_sha256": root["config_sha256"]}
            or descriptor["role_binding_sha256"] != c.file_hash(binding_path)
            or descriptor["base_model"]["manifest_sha256"] != c.pilot_recipe()["base_manifest_sha256"]
            or descriptor["base_model"]["path"] != c.pilot_recipe()["base_model"]):
        raise ValueError("service descriptor differs from fixed models/base")
    return {**old.planned_endpoint(binding), "url": f"http://{descriptor['host']}:{descriptor['port']}/v1",
            "api_key_env": descriptor["api_key_env"]}


def verify():
    spec = c.read(ROOT / "SPEC.json")
    c.authenticate(spec["source_file_sha256"])
    if spec["plan_sha256"] != c.digest(spec["plan"]) or spec["plan"] != build_plan(make_tasks()):
        raise ValueError("frozen triple plan changed")
    return spec


def phase_spec(binding_path, endpoint_path, destination, cap):
    spec = copy.deepcopy(verify())
    binding, descriptor = c.read(binding_path), c.read(endpoint_path)
    if binding != spec["binding"]:
        raise ValueError("service bound wrong policy")
    spec.update(endpoint=validate_descriptor(descriptor, binding, binding_path), role_binding=binding,
        binding_path=str(binding_path), endpoint_descriptor_path=str(endpoint_path),
        source_endpoint_descriptor=descriptor, wall_time_cap_seconds=min(cap, 2100),
        parent_spec_sha256=c.file_hash(ROOT / "SPEC.json"),
        serving_evidence=capture.recursive.serving_evidence(Path(endpoint_path).parent / "inference.log"))
    spec["source_file_sha256"].update({str(p):c.file_hash(p) for p in (binding_path, endpoint_path, ROOT/"SPEC.json", ROOT/"READY.json")})
    c.write_once(destination, spec)
    return spec


def verify_phase(path):
    spec = c.read(path)
    c.authenticate(spec["source_file_sha256"])
    parent = c.read(ROOT / "SPEC.json")
    for key in ("plan", "plan_sha256", "tasks", "environment", "image_id", "binding", "max_concurrent_pairs"):
        if spec[key] != parent[key]:
            raise ValueError("phase drift: " + key)
    if not 0 < spec["wall_time_cap_seconds"] <= 2100 or spec["parent_spec_sha256"] != c.file_hash(ROOT/"SPEC.json"):
        raise ValueError("phase cap or parent changed")
    if spec["endpoint"] != validate_descriptor(c.read(spec["endpoint_descriptor_path"]), spec["role_binding"], spec["binding_path"]):
        raise ValueError("phase endpoint changed")
    capture.recursive.validate_serving_evidence(spec["serving_evidence"])
    return spec
