"""Bounded native mixed-role collection; the coordinator owns the actual GPU service."""

import argparse
import asyncio
import copy
import json
import os
import sys
import urllib.request
from pathlib import Path

from credit_data import ROOT, digest, file_hash, load, read
from native_routing import installed_hooks, write_once

ROLE = ROOT.parent / "leaf-role-routing-v1"
sys.path.insert(0, str(ROLE / "source"))
role = load("root_credit_role_driver", ROLE / "source/driver.py")
recursive = load("root_credit_recursive_helpers", ROOT.parent / "recursive-train-capture-v1/driver.py")
native, q, base = recursive.native, role.q, role.old.base
ENDPOINT = ROLE / "service-attempt-001/endpoint-original.json"
BINDING = ROLE / "BOUND_WEIGHTS.json"
SERVER_LOG = ROLE / "service-attempt-001/inference.log"


def make_tasks():
    from oolong_prime_rlm_strict_v1.taskset import StrictOolongConfig, StrictOolongTask
    from oolong_prime_v1.taskset import _QUESTION_INSTRUCTION, _RLM_FILE_INSTRUCTION, OolongData
    from tokenizers import Tokenizer

    public, gold = read(ROOT / "inputs/PUBLIC.json"), read(ROOT / "inputs/HOST_GOLD.json")
    provenance = read(ROOT / "inputs/PROVENANCE.json")
    contexts = {c["id"]: c for c in public["contexts"]}
    tokenizer = Tokenizer.from_file(str(Path(read(ENDPOINT)["base_model"]["path"]) / "tokenizer.json"))
    tasks = {}
    for index, row in enumerate(public["tasks"]):
        context = contexts[row["context_id"]]["text"]
        data = OolongData(idx=index, name=row["name"],
            prompt=_QUESTION_INSTRUCTION + "\n\n" + _RLM_FILE_INSTRUCTION + "\n\nQuestion: " + row["question"],
            source_id=row["source_id"], source_split="official-TREC-source-train-local-root-" + row["split"],
            source_revision=provenance["source_split_sha256"], dataset=ROOT.name,
            context_len=len(tokenizer.encode(context, add_special_tokens=False).ids),
            context_window_id=row["context_window_id"], answer=gold[row["name"]]["answer"],
            answer_type=row["answer_type"], task_kind="local-count-by-coarse-category", context=context)
        tasks[row["name"]] = StrictOolongTask(data, StrictOolongConfig().task)
    return tasks


def binding():
    frozen = read(BINDING)
    return {**frozen, "fixed_child": role.SELECTED}


def make_context(endpoint, row):
    context = native.make_context(endpoint, row)
    if context.client.type != "train":
        raise ValueError("native train context required")
    return context


def prepare():
    tasks = make_tasks()
    descriptor = read(ENDPOINT)
    endpoint = {"url": f"http://{descriptor['host']}:{descriptor['port']}/v1",
        "model": descriptor["model_alias"], "api_key_env": descriptor["api_key_env"],
        "renderer_model": descriptor["base_model"]["path"]}
    plan = [{**r, "task_hash": role.with_prompt(tasks[r["task_name"]], "sft_child").hash}
            for r in read(ROOT / "inputs/PLAN.json")]
    bound = binding()
    spec = role.make_spec(endpoint, bound, tasks, plan, ROOT.name)
    for task in spec["tasks"]:
        task["arms"] = {"sft_child": task["arms"]["sft_child"]}
    spec.update(source_endpoint_descriptor=descriptor, coordinate_plan_sha256=digest(plan),
        observed_runtime_image_id=spec["image_id"].removeprefix("sha256:"),
        role_binding=bound, role_binding_file_sha256=file_hash(BINDING),
        serving_evidence=recursive.serving_evidence(SERVER_LOG),
        request_template=native.request_metadata(endpoint, plan[0]),
        interpretation="Fresh root-only credit with fixed validation-selected child; child actions are evidence/context, never targets.",
        credit_policy="Depth0 current native actions only; exact physical prefixes. Prior root/child/tool tokens masked. All-role raw evidence retained.",
        reward_policy="Complete observable wrong/malformed policy outputs=0; infrastructure/incomplete capture=null; no arbitrary action-shape filter.",
        training_policy="No optimization in Phase1; complete training split mixed groups only for separately declared Phase2.",
        partial_trace_limitation="Inherited collector may discard partial traces on infrastructure/cancellation failures; exclusions remain null rewards, never manufactured negatives.",
        split_provenance=read(ROOT / "inputs/PROVENANCE.json"),
        wall_time_cap_seconds=1800, max_concurrent_pairs=4)
    sources = [ROOT / n for n in ("credit_data.py", "native_routing.py", "root_export.py", "capture.py", "qualify_native.py", "test_phase1.py", "DESIGN.md", "PLAN.md")]
    sources += list((ROOT / "inputs").glob("*.json"))
    sources += [ENDPOINT, BINDING, Path(recursive.__file__), Path(native.__file__),
        Path(recursive.exporter.__file__), Path(recursive.exporter.analysis.__file__), recursive.exporter.TRAINER,
        q.PRIME / "deps/verifiers/verifiers/v1/clients/train.py",
        q.PRIME / "deps/renderers/renderers/client.py", q.PRIME / "deps/renderers/renderers/qwen3.py",
        q.PRIME / "deps/verifiers/verifiers/v1/trace.py", q.PRIME / "deps/verifiers/verifiers/v1/graph.py"]
    qualification = read(ROOT / "qualification-attempt-001/RESULT.json")
    if qualification.get("provider_calls") != 3 or qualification.get("credited_root_calls") != 2 or qualification.get("gpu_calls") != 0:
        raise ValueError("real CPU root-child-root native proof required before readiness")
    spec["cpu_qualification"] = qualification
    sources += [p for p in (ROOT / "qualification-attempt-001").rglob("*.json") if p.is_file()]
    spec["source_file_sha256"].update({str(p): file_hash(p) for p in sources})
    spec["source_file_sha256"].update(spec["split_provenance"]["source_sha256"])
    for source, expected in spec["source_file_sha256"].items():
        if file_hash(source) != expected:
            raise ValueError(f"source changed: {source}")
    write_once(ROOT / "SPEC.json", spec)
    return spec


def verify():
    spec = read(ROOT / "SPEC.json")
    for source, expected in spec["source_file_sha256"].items():
        if file_hash(source) != expected:
            raise ValueError(f"source changed: {source}")
    recursive.validate_serving_evidence(spec["serving_evidence"])
    for model in spec["role_binding"]["models"].values():
        path = Path(model["path"])
        if file_hash(path / "adapter_model.safetensors") != model["adapter_sha256"] or file_hash(path / "adapter_config.json") != model["config_sha256"]:
            raise ValueError("bound adapter changed")
    return spec


async def run(output):
    spec = verify()
    tasks = make_tasks()
    endpoint = spec["endpoint"]
    request = urllib.request.Request(endpoint["url"] + "/models",
        headers={"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]})
    with urllib.request.urlopen(request, timeout=15) as response:
        cards = {r["id"]: r for r in json.load(response)["data"]}
    for alias, model in spec["role_binding"]["models"].items():
        card = cards.get(alias, {})
        if Path(card.get("root", "")).resolve() != Path(model["path"]).resolve() or card.get("parent") != endpoint["renderer_model"]:
            raise ValueError("live alias/root/parent binding mismatch")
    os.environ["PATH"] = str(q.ROOTLESS / "bin") + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    audit = output.with_name(output.name + "-routing")
    if output.exists() or audit.exists():
        raise ValueError("new capture requires unused output/audit paths")
    write_once(audit / "BINDING.json", {"binding": spec["role_binding"], "advertised": cards})
    saved = (q.make_context, q.request_metadata, base.with_prompt, base.crossover_metrics, base.summarize, base.STUDY)
    q.make_context, q.request_metadata = make_context, native.request_metadata
    base.with_prompt, base.crossover_metrics = role.with_prompt, native.episode_metrics
    base.summarize = lambda records, plan: native.summarize(records, len(plan))
    base.STUDY = ROOT.name
    try:
        with installed_hooks(spec["role_binding"], audit):
            return await base.run(argparse.Namespace(endpoint_url=None, output_dir=output, resume=False), copy.deepcopy(spec), tasks)
    finally:
        q.make_context, q.request_metadata, base.with_prompt, base.crossover_metrics, base.summarize, base.STUDY = saved


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify", "run"))
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/attempt-001")
    args = parser.parse_args()
    if args.command == "run":
        raise SystemExit(asyncio.run(run(args.output.resolve())))
    spec = prepare() if args.command == "prepare" else verify()
    print(json.dumps({"planned": len(spec["plan"]), "plan_sha256": spec["plan_sha256"], "gpu_calls": 0}))


if __name__ == "__main__":
    main()
