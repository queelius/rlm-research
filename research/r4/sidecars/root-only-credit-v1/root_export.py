"""Exact physical branch reconstruction, mixed-role validation, depth0-only credit."""

import math

from credit_data import ROOT, digest, file_hash, read


def admitted_reward(completed, observable, strict_reward, capture_valid):
    return strict_reward if completed and observable and capture_valid and type(strict_reward) is int and strict_reward in (0, 1) else None


def causal_root_turns(trace, roles, *, root_alias, child_alias):
    indices = {id(node): index for index, node in enumerate(trace.nodes)}
    calls = {}
    for call_index, call in enumerate(trace.calls):
        if call.error or call.node is None or call.node in calls or not 0 <= call.node < len(trace.nodes):
            raise ValueError("failed/duplicate/unpreserved call")
        role = roles.get(call.node)
        if not role or role["depth"] not in (0, 1):
            raise ValueError("call lacks trusted role audit")
        expected = root_alias if role["depth"] == 0 else child_alias
        if call.model != expected or role["actual_alias"] != expected:
            raise ValueError("actual call alias and trusted role differ")
        sampling = call.sampling
        if sampling is None or (sampling.temperature, sampling.top_p, sampling.top_k, sampling.min_p) != (0.5, 1.0, -1, 0.0):
            raise ValueError("actual role sampling differs from declared full support")
        calls[call.node] = (call_index, call, role)
    sampled = {i for i, node in enumerate(trace.nodes) if node.sampled}
    if not sampled or set(calls) != sampled:
        raise ValueError("call/sample-node correspondence is not one-to-one")
    exported = {}
    for branch in trace.branches:
        prefix = []
        for node in branch.nodes:
            index = indices[id(node)]
            ids, mask, logs = node.token_ids, node.mask, node.logprobs
            if len(ids) != len(mask) or any(type(i) is not int or i < 0 for i in ids) or any(type(m) is not bool for m in mask):
                raise ValueError("invalid exact native graph tokens/masks")
            count = sum(mask)
            if len(logs) != count or any(isinstance(x, bool) or not math.isfinite(x) or x > 0 or x == -9999 for x in logs):
                raise ValueError("invalid/misaligned sampled logprobs")
            if not node.sampled and count:
                raise ValueError("environment observation has action credit")
            if node.sampled:
                if not count or mask != [False] * (len(ids) - count) + [True] * count:
                    raise ValueError("sampled action is not a nonempty suffix")
                call_index, call, role = calls[index]
                sequence = prefix + ids
                prompt = len(sequence) - count
                if not prompt or call.usage is None or call.usage.input_tokens != prompt or call.usage.completion_tokens != count:
                    raise ValueError("physical prefix/action differs from actual call usage")
                row = {"input_ids": sequence, "labels": [-100] * prompt + sequence[prompt:],
                    "loss_mask": [0] * prompt + [1] * count, "old_logprobs": list(logs),
                    "prompt_length": prompt, "source_trace_id": trace.id, "source_node_index": index,
                    "source_call_index": call_index, "sampling": call.sampling.model_dump(mode="json", exclude_none=True),
                    "call_model": call.model, "call_finish_reason": call.finish_reason,
                    "usage_input_tokens": prompt, "usage_completion_tokens": count,
                    "role_depth": role["depth"], "role_audit": role,
                    "credited": role["depth"] == 0}
                if index in exported and exported[index] != row:
                    raise ValueError("shared sampled node has inconsistent causal prefix")
                exported[index] = row
            prefix.extend(ids)
        if prefix != branch.token_ids:
            raise ValueError("official branch flattening mismatch")
    if set(exported) != sampled:
        raise ValueError("sampled call unreachable from official physical branches")
    evidence = [exported[i] for i in sorted(exported)]
    return [r for r in evidence if r["credited"]], evidence


def episode_turns(episode, audit_path, binding):
    from verifiers.v1.trace import WireTrace

    audits = {}
    for path in (audit_path / "role-audit").glob("*-result.json"):
        audit = read(path)
        request_id = audit.get("request_id")
        if request_id in audits:
            raise ValueError("duplicate role audit request identity")
        audits[request_id] = (audit, path)
    root_turns, all_turns, seen = [], [], set()
    for raw in episode.get("traces", []):
        if raw["agent"]["config"]["client"].get("renderer") != {"name": "qwen3", "enable_thinking": True}:
            raise ValueError("actual trace renderer differs")
        trace = WireTrace.model_validate(raw)
        if trace.id in seen or trace.errors or not trace.ok or not trace.is_completed:
            raise ValueError("duplicate/failed/incomplete trace")
        seen.add(trace.id)
        roles = {}
        raw_by_node = {}
        for call in raw["calls"]:
            request_id = (call.get("acp") or {}).get("request_id")
            if request_id not in audits:
                raise ValueError("committed call lacks real request-local audit")
            audit, path = audits[request_id]
            if audit["status"] != "returned" or audit["actual_alias"] != call["model"]:
                raise ValueError("failed audit or actual trace model mismatch")
            expected = binding["models"][audit["actual_alias"]]["adapter_sha256"]
            if audit["model_sha256"] != expected:
                raise ValueError("audit weight binding differs")
            roles[call["node"]] = {k: audit[k] for k in ("depth", "actual_alias", "request_id", "invocation", "model_sha256")}
            roles[call["node"]].update(source_audit_path=str(path), source_audit_sha256=file_hash(path))
            raw_by_node[call["node"]] = audit
        roots, evidence = causal_root_turns(trace, roles, root_alias=binding["role_map"]["root"], child_alias=binding["fixed_child"])
        root_invocations = {r["invocation"] for r in roles.values() if r["depth"] == 0}
        if len(root_invocations) != 1:
            raise ValueError("trace must have exactly one root invocation identity")
        for item in evidence:
            audit = raw_by_node[item["source_node_index"]]
            tokens = audit["native_response"]["tokens"]
            wire = audit["native_wire_request"]["body"]
            raw_response = audit["native_wire_response"]
            if raw_response["http_status"] != 200:
                raise ValueError("native response not successful")
            import json
            choice = json.loads(raw_response["body"])["choices"][0]
            if (tokens["prompt_ids"] + tokens["completion_ids"] != item["input_ids"]
                    or tokens["completion_logprobs"] != item["old_logprobs"]
                    or wire["token_ids"] != tokens["prompt_ids"]
                    or wire["model"] != item["call_model"]
                    or choice["token_ids"] != tokens["completion_ids"]
                    or [r["logprob"] for r in choice["logprobs"]["content"]] != item["old_logprobs"]):
                raise ValueError("physical graph differs from native raw request/response tokens")
            for key, expected in {"temperature": 0.5, "top_p": 1, "top_k": -1, "min_p": 0, "max_tokens": 2048}.items():
                if wire["sampling_params"].get(key) != expected or item["sampling"].get(key) != expected:
                    raise ValueError("native wire/graph sampling mismatch")
            if wire["sampling_params"]["seed"] != item["sampling"]["seed"]:
                raise ValueError("native wire/graph seed mismatch")
        for index, node in enumerate(trace.nodes):
            for link in raw["nodes"][index].get("semantic_parents", []):
                if index not in roles or link["node"] not in roles:
                    continue
                if link["type"] == "subagent_call" and (roles[index]["depth"], roles[link["node"]]["depth"]) != (1, 0):
                    raise ValueError("semantic child call contradicts trusted depth")
                if link["type"] == "subagent_return" and (roles[index]["depth"], roles[link["node"]]["depth"]) != (0, 1):
                    raise ValueError("semantic child return contradicts trusted depth")
        root_turns.extend(roots)
        all_turns.extend(evidence)
    if not root_turns:
        raise ValueError("no complete native root actions")
    return root_turns, all_turns


def export_attempt(attempt, output):
    import json
    from collections import Counter, defaultdict
    import capture
    from native_routing import write_once

    spec = capture.verify()
    if read(attempt / "SPEC.json") != spec:
        raise ValueError("attempt does not match frozen Phase1 source")
    audit_path = attempt.with_name(attempt.name + "-routing")
    plan = {r["id"]: r for r in spec["plan"]}
    records = [(path, read(path)) for path in sorted((attempt / "episodes").glob("*.json"))]
    complete = len(records) == len(plan)
    provenance = {"source_attempt": str(attempt), "source_spec_sha256": file_hash(attempt / "SPEC.json"),
        "source_record_sha256": {path.stem: file_hash(path) for path, _ in records},
        "plan_sha256": spec["plan_sha256"], "complete": complete,
        "credit_policy": spec["credit_policy"], "role_binding": spec["role_binding"],
        "serving_evidence": spec["serving_evidence"]}
    dataset_id = digest(provenance)
    rows = []
    for path, record in records:
        coordinate = record["coordinate"]
        if coordinate != plan[path.stem] or digest(record["episode"]) != record["episode_sha256"]:
            raise ValueError("raw episode/coordinate identity changed")
        metrics = capture.native.episode_metrics(record["episode"], record["timing"]["wall_seconds"])
        row = {"episode_id": coordinate["id"], "task_id": coordinate["task_name"],
            "cell_id": "original-root-fixed-sft-child", "split": coordinate["split"],
            "sample_seed": coordinate["seed"], "temperature": 0.5, "dataset_id": dataset_id,
            "execution_completed": metrics["execution_completed"], "terminal_observable": metrics["terminal_observable"],
            "terminal_schema_valid": metrics["strict_terminal_valid"], "terminal_correct": metrics["strict_correct"],
            "strict_reward": metrics["strict_reward"], "reward": None, "trace_trainable": False,
            "turns": [], "all_role_evidence": [], "invalid_reason": None,
            "provenance": {"raw_episode_sha256": record["episode_sha256"], "source_record_sha256": file_hash(path),
                "role_binding": spec["role_binding"], "base_model": spec["source_endpoint_descriptor"]["base_model"],
                "adapter": spec["source_endpoint_descriptor"]["adapter"], "credit_policy": spec["credit_policy"],
                "rollout_logprobs_mode": "processed_logprobs", "renderer": {"name": "qwen3", "enable_thinking": True},
                "runtime_image_id": spec["observed_runtime_image_id"]}}
        try:
            roots, evidence = episode_turns(record["episode"], audit_path, spec["role_binding"])
            if len(evidence) != metrics["model_calls"] or any(t["sampling"]["seed"] != coordinate["seed"] for t in evidence):
                raise ValueError("actual call count/seed differs from frozen coordinate")
            row["all_role_evidence"] = evidence
            reward = admitted_reward(metrics["execution_completed"], metrics["terminal_observable"], metrics["strict_reward"], metrics["trace_trainable"])
            if reward is None:
                raise ValueError("incomplete/unobservable/failed capture; not a policy negative")
            row.update(turns=roots, reward=reward, trace_trainable=True,
                action_tokens=sum(len(t["old_logprobs"]) for t in roots), turn_count=len(roots),
                child_action_tokens=sum(len(t["old_logprobs"]) for t in evidence if not t["credited"]))
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            row["invalid_reason"] = str(error)
        rows.append(row)
    group, group_reason = None, "collection_incomplete"
    if complete:
        training = [row for row in rows if row["split"] == "training"]
        try:
            group = capture.recursive.exporter.trainer_module().training_group(training)
            group["credit_policy"] = spec["credit_policy"]
            group["dataset_id"] = dataset_id
            group["role_binding"] = spec["role_binding"]
            group["group_id"] = digest({k: v for k, v in group.items() if k != "group_id"})
            group_reason = None
        except ValueError as error:
            if str(error) != "no fresh within-prompt mixed reward group":
                raise
            group_reason = str(error)
    tasks = defaultdict(list)
    for row in rows:
        tasks[row["task_id"]].append(row)
    manifest = {"schema": ROOT.name + "-export", "dataset_id": dataset_id, **provenance,
        "recorded": len(rows), "planned": len(plan), "trainable": sum(r["trace_trainable"] for r in rows),
        "invalid_reasons": dict(Counter(r["invalid_reason"] for r in rows if r["invalid_reason"])),
        "tasks": [{"task": name, "split": values[0]["split"], "rewards": [r["reward"] for r in values],
                   "mixed": {r["reward"] for r in values if r["trace_trainable"]} == {0, 1}} for name, values in sorted(tasks.items())],
        "training_group_episodes": len(group["episodes"]) if group else 0, "training_group_unavailable_reason": group_reason,
        "root_action_tokens": sum(r.get("action_tokens", 0) for r in rows),
        "child_evidence_never_targets": True, "new_update_authorized": False}
    output.mkdir(parents=True, exist_ok=False)
    with (output / "episodes.jsonl").open("x") as stream:
        for row in rows:
            stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
    if group:
        write_once(output / "training-group.json", group)
    manifest["artifact_sha256"] = {p.name: file_hash(p) for p in output.iterdir()}
    write_once(output / "MANIFEST.json", manifest)
    print(json.dumps({"complete": complete, "recorded": len(rows), "training_group_episodes": manifest["training_group_episodes"], "group_reason": group_reason}), flush=True)


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    export_attempt(args.attempt.resolve(), args.output.resolve())
