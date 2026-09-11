"""Qualified native collection and exact root-only export with explicit campaign binding."""

import argparse
import asyncio
import copy
import json
import os
import sys
import urllib.request
from collections import Counter
from pathlib import Path

import campaign_common as c

sys.path.insert(0, str(c.PILOT))
capture = c.load("campaign_qualified_capture", c.PILOT / "capture.py")
exporter = c.load("campaign_qualified_exporter", c.PILOT / "root_export.py")


def make_tasks():
    from oolong_prime_rlm_strict_v1.taskset import StrictOolongConfig, StrictOolongTask
    from oolong_prime_v1.taskset import _QUESTION_INSTRUCTION, _RLM_FILE_INSTRUCTION, OolongData
    from tokenizers import Tokenizer

    tasks = capture.make_tasks()  # Original prompt/context/task construction stays byte-identical.
    public = c.read(c.ROOT / "inputs/TRANSFER_PUBLIC.json")
    gold = c.read(c.ROOT / "inputs/TRANSFER_HOST_GOLD.json")
    contexts = {row["id"]: row for row in public["contexts"]}
    tokenizer = Tokenizer.from_file(str(Path(c.pilot_recipe()["base_model"]) / "tokenizer.json"))
    for index, row in enumerate(public["tasks"]):
        context = contexts[row["context_id"]]["text"]
        data = OolongData(idx=index + 100, name=row["name"],
            prompt=_QUESTION_INSTRUCTION + "\n\n" + _RLM_FILE_INSTRUCTION + "\n\nQuestion: " + row["question"],
            source_id=row["source_id"], source_split="official-TREC-source-train-root-transfer",
            source_revision=c.read(c.ROOT / "inputs/PROVENANCE.json")["source_split_sha256"],
            dataset=c.ROOT.name, context_len=len(tokenizer.encode(context, add_special_tokens=False).ids),
            context_window_id=row["context_window_id"], answer=gold[row["name"]]["answer"],
            answer_type=row["answer_type"], task_kind="local-count-by-coarse-category", context=context)
        tasks[row["name"]] = StrictOolongTask(data, StrictOolongConfig().task)
    return tasks


def task_identity(tasks):
    import hashlib
    return {name: {"task_hash": capture.role.with_prompt(task, "sft_child").hash,
                   "prompt_sha256": hashlib.sha256(capture.role.with_prompt(task, "sft_child").data.prompt.encode()).hexdigest(),
                   "context_sha256": hashlib.sha256(task.data.context.encode()).hexdigest()}
            for name, task in tasks.items()}


def binding_for(policy):
    c.authenticate_policy(policy)
    old = c.read(c.ROLE / "BOUND_WEIGHTS.json")
    child_alias = capture.role.SELECTED
    child = old["models"][child_alias]
    if child["adapter_sha256"] != c.CHILD_SHA:
        raise ValueError("selected child changed")
    root_alias = f"strict-rlm-qwen3-4b-campaign-root-step{policy['step']}-v1"
    binding = {**old, "models": {root_alias: {"path": policy["path"],
        "adapter_sha256": policy["adapter_sha256"], "config_sha256": policy["config_sha256"]}, child_alias: child},
        "role_map": {"root": root_alias, "children": [child_alias]}, "fixed_child": child_alias,
        "campaign_policy": policy, "campaign_id": c.verify_campaign()["campaign_id"]}
    authenticate_binding(binding)
    return binding


def authenticate_binding(binding):
    if binding["fixed_child"] not in binding["role_map"]["children"]:
        raise ValueError("fixed child is not bound")
    child = binding["models"][binding["fixed_child"]]
    expected_child = c.read(c.ROLE / "BOUND_WEIGHTS.json")["models"][capture.role.SELECTED]
    if (binding["fixed_child"] != capture.role.SELECTED or child != expected_child
            or child["adapter_sha256"] != c.CHILD_SHA or len(binding["models"]) != 2):
        raise ValueError("campaign requires exactly current root and fixed selected child")
    policy = binding["campaign_policy"]
    root = binding["models"][binding["role_map"]["root"]]
    if root != {"path": policy["path"], "adapter_sha256": policy["adapter_sha256"], "config_sha256": policy["config_sha256"]}:
        raise ValueError("role root differs from current policy")
    c.authenticate_policy(policy)
    for model in binding["models"].values():
        c.authenticate({Path(model["path"]) / "adapter_model.safetensors": model["adapter_sha256"],
                        Path(model["path"]) / "adapter_config.json": model["config_sha256"]})
    c.authenticate({binding["selection_path"]: binding["selection_sha256"]})


def planned_rows(phase):
    plans = c.read(c.ROOT / "inputs/PLANS.json")
    if phase.startswith("round-"):
        return plans["training"][str(int(phase.split("-")[1]))]
    if phase.startswith("validation-"):
        return plans["validation"]
    return plans[phase.replace("-", "_")]


def prepare_spec(phase, binding_path, endpoint_path, destination, cap, generation=None):
    campaign = c.verify_campaign()
    binding, descriptor = c.read(binding_path), c.read(endpoint_path)
    authenticate_binding(binding)
    root = binding["models"][binding["role_map"]["root"]]
    if (descriptor["model_alias"] != binding["role_map"]["root"]
            or descriptor["adapter"] != {"path": root["path"], "model_sha256": root["adapter_sha256"], "config_sha256": root["config_sha256"]}
            or descriptor["role_binding_sha256"] != c.file_hash(binding_path)
            or descriptor["base_model"]["manifest_sha256"] != c.pilot_recipe()["base_manifest_sha256"]):
        raise ValueError("actual endpoint descriptor does not bind the current root/base/config")
    tasks = make_tasks()
    if task_identity(tasks) != c.read(c.ROOT / "inputs/TASK_IDENTITIES.json"):
        raise ValueError("frozen task/prompt/context identity changed")
    rows = planned_rows(phase)
    if generation is not None:
        c.check_generation(generation, binding["campaign_policy"], binding["campaign_policy"]["step"])
        if generation["coordinate_plan_sha256"] != c.digest(rows) or generation["campaign_id"] != campaign["campaign_id"]:
            raise ValueError("generation coordinates differ from campaign")
    plan = [{**row, "task_hash": capture.role.with_prompt(tasks[row["task_name"]], "sft_child").hash} for row in rows]
    tasks = {row["task_name"]: tasks[row["task_name"]] for row in rows}
    endpoint = {"url": f"http://{descriptor['host']}:{descriptor['port']}/v1", "model": descriptor["model_alias"],
                "api_key_env": descriptor["api_key_env"], "renderer_model": descriptor["base_model"]["path"]}
    spec = capture.role.make_spec(endpoint, binding, tasks, plan, c.ROOT.name)
    for task in spec["tasks"]:
        task["arms"] = {"sft_child": task["arms"]["sft_child"]}
    pilot = c.read(c.PILOT / "SPEC.json")
    spec.update(campaign_id=campaign["campaign_id"], campaign_phase=phase, generation=generation,
        endpoint_descriptor_path=str(Path(endpoint_path).resolve()), binding_path=str(Path(binding_path).resolve()),
        campaign_policy=binding["campaign_policy"], coordinate_plan_sha256=c.digest(rows),
        source_endpoint_descriptor=descriptor, role_binding=binding,
        role_binding_file_sha256=c.file_hash(binding_path),
        observed_runtime_image_id=spec["image_id"].removeprefix("sha256:"),
        serving_evidence=capture.recursive.serving_evidence(Path(endpoint_path).parent / "inference.log"),
        request_template=capture.native.request_metadata(endpoint, plan[0]),
        wall_time_cap_seconds=cap, max_concurrent_pairs=c.read(c.ROOT / "RECIPE.json")["max_concurrent_pairs"],
        role_policy={"depth0": binding["role_map"]["root"], "depth1": binding["fixed_child"], "missing_metadata": "observable failure", "decoder_constraint": None},
        interpretation="Fresh root-only generation; fixed selected child; validation/transfer never training inputs.",
        credit_policy=pilot["credit_policy"], reward_policy=pilot["reward_policy"],
        partial_trace_limitation=pilot["partial_trace_limitation"])
    spec["source_file_sha256"].update(campaign["source_sha256"])
    spec["source_file_sha256"].update(campaign["input_sha256"])
    spec["source_file_sha256"].update({str(p): c.file_hash(p) for p in
        [Path(binding_path), Path(endpoint_path), c.ROOT / "CAMPAIGN.json", c.ROOT / "READY.json"]})
    c.write_once(destination, spec)
    return spec


def verify_spec(path):
    campaign = c.verify_campaign()
    spec = c.read(path)
    c.authenticate(spec["source_file_sha256"])
    expected_sources = {**campaign["source_sha256"], **campaign["input_sha256"]}
    if any(spec["source_file_sha256"].get(p) != sha for p, sha in expected_sources.items()):
        raise ValueError("capture dropped a frozen campaign source/input authentication")
    pilot = c.read(c.PILOT / "SPEC.json")
    if (spec["environment"] != pilot["environment"] or spec["image_id"] != pilot["image_id"]
            or spec["credit_policy"] != pilot["credit_policy"] or spec["reward_policy"] != pilot["reward_policy"]
            or spec["max_concurrent_pairs"] != c.read(c.ROOT / "RECIPE.json")["max_concurrent_pairs"]):
        raise ValueError("qualified environment/image/objective/concurrency contract changed")
    descriptor = c.read(spec["endpoint_descriptor_path"])
    binding = c.read(spec["binding_path"])
    root = binding["models"][binding["role_map"]["root"]]
    expected_endpoint = {"url": f"http://{descriptor['host']}:{descriptor['port']}/v1",
        "model": binding["role_map"]["root"], "api_key_env": descriptor["api_key_env"],
        "renderer_model": c.pilot_recipe()["base_model"]}
    if (binding != spec["role_binding"] or descriptor != spec["source_endpoint_descriptor"]
            or descriptor["adapter"] != {"path": root["path"], "model_sha256": root["adapter_sha256"], "config_sha256": root["config_sha256"]}
            or descriptor["model_alias"] != binding["role_map"]["root"]
            or descriptor["role_binding_sha256"] != c.file_hash(spec["binding_path"])
            or spec["endpoint"] != expected_endpoint or binding["campaign_policy"] != spec["campaign_policy"]):
        raise ValueError("actual descriptor/role/policy binding changed")
    if spec["campaign_id"] != campaign["campaign_id"] or spec["plan_sha256"] != c.digest(spec["plan"]):
        raise ValueError("capture campaign/plan identity changed")
    if spec["coordinate_plan_sha256"] != c.digest(planned_rows(spec["campaign_phase"])):
        raise ValueError("capture coordinates not from frozen campaign")
    expected = [{**r, "task_hash": c.read(c.ROOT / "inputs/TASK_IDENTITIES.json")[r["task_name"]]["task_hash"]}
                for r in planned_rows(spec["campaign_phase"])]
    if spec["plan"] != expected:
        raise ValueError("capture plan has altered task identity or seed")
    tasks = make_tasks()
    identities = task_identity(tasks)
    if identities != c.read(c.ROOT / "inputs/TASK_IDENTITIES.json"):
        raise ValueError("actual task/prompt/context reconstruction changed")
    task_specs = {t["name"]: t for t in spec["tasks"]}
    if set(task_specs) != {r["task_name"] for r in expected}:
        raise ValueError("unexpected task scope")
    for name, task in task_specs.items():
        if (task["context_sha256"] != identities[name]["context_sha256"]
                or task["arms"] != {"sft_child": {"task_hash": identities[name]["task_hash"],
                    "prompt": capture.role.with_prompt(tasks[name], "sft_child").data.prompt}}):
            raise ValueError("actual executable-example/public-definition prompt changed")
    authenticate_binding(spec["role_binding"])
    capture.recursive.validate_serving_evidence(spec["serving_evidence"])
    if spec["generation"] is not None:
        c.check_generation(spec["generation"], spec["campaign_policy"], spec["campaign_policy"]["step"])
    return spec


async def collect(spec_path, output):
    spec = verify_spec(spec_path)
    if output.exists() or output.with_name(output.name + "-routing").exists():
        raise ValueError("capture attempt paths must be unused; no implicit failed-attempt retry")
    endpoint = spec["endpoint"]
    request = urllib.request.Request(endpoint["url"] + "/models", headers={"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]})
    with urllib.request.urlopen(request, timeout=15) as response:
        cards = {row["id"]: row for row in json.load(response)["data"]}
    for alias, model in spec["role_binding"]["models"].items():
        card = cards.get(alias, {})
        if Path(card.get("root", "")).resolve() != Path(model["path"]).resolve() or card.get("parent") != endpoint["renderer_model"]:
            raise ValueError("live /models alias/root/parent mismatch")
    os.environ["PATH"] = str(capture.q.ROOTLESS / "bin") + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    audit = output.with_name(output.name + "-routing")
    c.write_once(audit / "BINDING.json", {"binding": spec["role_binding"], "advertised": cards})
    tasks = make_tasks()
    tasks = {r["task_name"]: tasks[r["task_name"]] for r in spec["plan"]}
    q, base = capture.q, capture.base
    saved = q.make_context, q.request_metadata, base.with_prompt, base.crossover_metrics, base.summarize, base.STUDY
    q.make_context, q.request_metadata = capture.make_context, capture.native.request_metadata
    base.with_prompt, base.crossover_metrics = capture.role.with_prompt, capture.native.episode_metrics
    base.summarize = lambda records, plan: capture.native.summarize(records, len(plan))
    base.STUDY = c.ROOT.name
    try:
        with capture.installed_hooks(spec["role_binding"], audit):
            return await base.run(argparse.Namespace(endpoint_url=None, output_dir=output, resume=False), copy.deepcopy(spec), tasks)
    finally:
        q.make_context, q.request_metadata, base.with_prompt, base.crossover_metrics, base.summarize, base.STUDY = saved


def rebuild_export(attempt):
    spec = verify_spec(attempt / "SPEC.json")
    plan = {r["id"]: r for r in spec["plan"]}
    records = [(p, c.read(p)) for p in sorted((attempt / "episodes").glob("*.json"))]
    if {p.stem for p, _ in records} != plan.keys():
        raise ValueError("collection incomplete or extra coordinates; cannot advance campaign")
    provenance = {"source_attempt": str(attempt), "source_spec_sha256": c.file_hash(attempt / "SPEC.json"),
        "source_record_sha256": {p.stem: c.file_hash(p) for p, _ in records}, "campaign_id": spec["campaign_id"],
        "generation": spec["generation"], "role_binding": spec["role_binding"], "complete": True,
        "coordinate_plan_sha256": spec["coordinate_plan_sha256"], "serving_evidence": spec["serving_evidence"]}
    dataset_id = c.digest(provenance)
    rows, integrity_failures = [], []
    audit = attempt.with_name(attempt.name + "-routing")
    for path, record in records:
        coordinate = record["coordinate"]
        if coordinate != plan[path.stem] or c.digest(record["episode"]) != record["episode_sha256"]:
            raise ValueError("raw native episode/coordinate identity changed")
        metrics = capture.native.episode_metrics(record["episode"], record["timing"]["wall_seconds"])
        row = {"episode_id": path.stem, "task_id": coordinate["task_name"], "cell_id": spec["campaign_phase"],
            "split": coordinate["split"], "sample_seed": coordinate["seed"], "temperature": 0.5,
            "dataset_id": dataset_id, "execution_completed": metrics["execution_completed"],
            "terminal_observable": metrics["terminal_observable"], "terminal_schema_valid": metrics["strict_terminal_valid"],
            "terminal_correct": metrics["strict_correct"], "strict_reward": metrics["strict_reward"],
            "reward": None, "trace_trainable": False, "turns": [], "all_role_evidence": [], "invalid_reason": None,
            "metrics": metrics, "wall_seconds": record["timing"]["wall_seconds"],
            "provenance": {"raw_episode_sha256": record["episode_sha256"], "source_record_sha256": c.file_hash(path),
                "adapter": spec["source_endpoint_descriptor"]["adapter"], "role_binding": spec["role_binding"],
                "base_model": spec["source_endpoint_descriptor"]["base_model"], "rollout_logprobs_mode": "processed_logprobs",
                "runtime_image_id": spec["observed_runtime_image_id"], "renderer": {"name": "qwen3", "enable_thinking": True}}}
        try:
            roots, evidence = exporter.episode_turns(record["episode"], audit, spec["role_binding"])
            if len(evidence) != metrics["model_calls"] or any(t["sampling"]["seed"] != coordinate["seed"] for t in evidence):
                raise ValueError("actual call count/seed differs from frozen coordinate")
            row["all_role_evidence"] = evidence
            reward = c.reward_admission(metrics["execution_completed"], metrics["terminal_observable"], metrics["strict_reward"], metrics["trace_trainable"])
            if reward is None:
                raise ValueError("incomplete/unobservable capture is not a policy negative")
            row.update(turns=roots, reward=reward, trace_trainable=True,
                       action_tokens=sum(len(t["old_logprobs"]) for t in roots),
                       child_action_tokens=sum(len(t["old_logprobs"]) for t in evidence if not t["credited"]))
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            row["invalid_reason"] = str(error)
            if metrics["execution_completed"] and metrics["trace_trainable"]:
                integrity_failures.append({"episode_id": path.stem, "reason": str(error)})
        rows.append(row)
    group, reason = None, None
    if spec["generation"] is not None and not integrity_failures:
        try:
            group = capture.recursive.exporter.trainer_module().training_group(rows)
            group.update(dataset_id=dataset_id, role_binding=spec["role_binding"],
                         generation=spec["generation"], credit_policy=spec["credit_policy"])
            group["group_id"] = c.digest({k: v for k, v in group.items() if k != "group_id"})
        except ValueError as error:
            if str(error) != "no fresh within-prompt mixed reward group":
                raise
            reason = str(error)
    manifest = {**provenance, "dataset_id": dataset_id, "planned": len(plan), "recorded": len(rows),
        "strict_successes": sum(r["reward"] == 1 for r in rows),
        "admitted_outcomes": sum(r["reward"] is not None for r in rows), "integrity_failures": integrity_failures,
        "exclusion_reasons": dict(Counter(r["invalid_reason"] for r in rows if r["invalid_reason"])),
        "training_group_unavailable_reason": reason, "training_group_episodes": len(group["episodes"]) if group else 0,
        "root_action_tokens": sum(r.get("action_tokens", 0) for r in rows),
        "child_evidence_action_tokens": sum(r.get("child_action_tokens", 0) for r in rows)}
    return rows, group, manifest


def export(attempt, output):
    rows, group, manifest = rebuild_export(attempt)
    if output.exists():
        raise ValueError("export path already exists; verify it, do not overwrite")
    output.mkdir(parents=True)
    c.write_once(output / "EPISODES.json", rows)
    if group:
        c.write_once(output / "GROUP.json", group)
    manifest["artifact_sha256"] = {p.name: c.file_hash(p) for p in output.iterdir()}
    c.write_once(output / "MANIFEST.json", manifest)
    return manifest


def authenticate_export(output):
    manifest = c.read(output / "MANIFEST.json")
    c.authenticate({output / name: sha for name, sha in manifest["artifact_sha256"].items()})
    rows, group, rebuilt = rebuild_export(Path(manifest["source_attempt"]))
    if rows != c.read(output / "EPISODES.json") or rebuilt != {k: v for k, v in manifest.items() if k != "artifact_sha256"}:
        raise ValueError("exported outcomes differ from native raw evidence")
    if group is not None and group != c.read(output / "GROUP.json"):
        raise ValueError("mixed group/advantage differs from all native outcomes")
    if manifest["integrity_failures"]:
        raise ValueError("native identity/mask/capture integrity failure; campaign must stop")
    return {"manifest_sha256": c.file_hash(output / "MANIFEST.json"),
            "group_sha256": c.file_hash(output / "GROUP.json") if group else None,
            "replayed": len(rows), "selected": len(group["episodes"]) if group else 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("qualify-tasks", "collect", "export", "verify-export"))
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--attempt", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "qualify-tasks":
        value = task_identity(make_tasks())
        c.write_once(c.ROOT / "inputs/TASK_IDENTITIES.json", value)
        print(json.dumps({"tasks": len(value), "gpu_calls": 0}))
    elif args.command == "collect":
        raise SystemExit(asyncio.run(collect(args.spec.resolve(), args.output.resolve())))
    elif args.command == "export":
        print(json.dumps(export(args.attempt.resolve(), args.output.resolve())))
    else:
        print(json.dumps(authenticate_export(args.output.resolve())))
