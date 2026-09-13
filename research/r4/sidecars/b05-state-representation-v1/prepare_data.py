"""Freeze twelve new cases across raw, grouped-unresolved, and resolved public views."""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FRESH = ROOT.parent / "b05-public-normalization-fresh12-v1"
spec = importlib.util.spec_from_file_location("b05_state_repr_fresh_source", FRESH / "study.py")
fresh = importlib.util.module_from_spec(spec); spec.loader.exec_module(fresh)
represent = fresh.load("b05_state_repr_transform", ROOT / "represent.py")
NORMALIZE = fresh.PRIOR / "normalize.py"
normalize = fresh.load("b05_state_repr_normalizer", NORMALIZE)
IDS = ROOT.parent / "b05-eligible-ids-interface-v1"
with fresh.aliases({"study": fresh}, IDS):
    interface = fresh.load("b05_state_repr_id_contract", IDS / "interface.py")


def main():
    api = fresh.source.b05()
    previous = [fresh.SOURCE / "inputs/PUBLIC.json",
        fresh.ROOT.parents[1] / "ideas/b05-helper-width-feasibility-2026-09-12/public/PUBLIC.json",
        fresh.TRAIN / "HELD_PUBLIC.json", fresh.ROOT / "PUBLIC_ROOTS.json"]
    old_roots = [root.get("safe_root", root) for path in previous
                 for root in fresh.read(path)["roots"]]
    used_roots = {root["root_id"] for root in old_roots}
    used_ids = {item["implementation_id"] for root in old_roots for stage in root["stages"]
                for item in stage["tables"]["implementations"]}
    dimensions = [(1,6,0),(1,6,1),(1,12,2),(1,12,0),(1,20,1),(1,20,2),
                  (3,6,0),(3,6,1),(3,6,2),(3,12,0),(3,12,1),(3,12,2)]
    tasks, calls, prompts, requests, roots, children, token_rows = [], [], {}, {}, [], [], []
    for index, (history, width, stage_index) in enumerate(dimensions):
        generation_seed = 202609400000 + index
        root = api.generate(generation_seed, api.StructuralConfig(
            width, history, 1, 3, 1, "chain", "helper-width-local-v1"))
        assert root["root_id"] not in used_roots
        candidate_ids = {item["implementation_id"] for stage in root["stages"]
                         for item in stage["tables"]["implementations"]}
        assert not used_ids & candidate_ids
        used_roots.add(root["root_id"]); used_ids |= candidate_ids
        child = api.extract_child(root, stage_index); children.append(child)
        roots.append(api.build_safe_root_record(root))
        raw = interface.render(api.render_child(child))
        raw_view, _ = represent.public_view(raw)
        unresolved = represent.render_unresolved(raw)
        unresolved_view = represent.unresolved_view(raw_view)
        resolved = normalize.render(raw)
        resolved_view = normalize.normalized_view(raw_view)
        known = sorted(item["implementation_id"] for item in child["stage"]["tables"]["implementations"])
        tasks.append({"root_id": root["root_id"], "width": width, "history_depth": history,
            "check_revisions": 1, "generation_seed": generation_seed, "selected_stage": stage_index,
            "known_ids": known, "raw_prompt": raw, "raw_public_view": raw_view,
            "unresolved_prompt": unresolved, "unresolved_public_view": unresolved_view,
            "resolved_prompt": resolved, "resolved_public_view": resolved_view})
        for repeat in (0, 1):
            seed = 202609410000 + 2*index + repeat
            order = ("raw", "unresolved", "resolved")
            shift = (index + repeat) % 3
            for arm in order[shift:] + order[:shift]:
                call = {"root_id": root["root_id"], "width": width,
                    "history_depth": history, "repeat": repeat, "arm": arm,
                    "kind": "selection", "seed": seed, "max_tokens": 384}
                prompt = {"raw": raw, "unresolved": unresolved, "resolved": resolved}[arm]
                key = fresh.call_id(call); body = fresh.request_body(prompt, seed, 384)
                calls.append(call); prompts[key] = prompt; requests[key] = body
                token_rows.append({"call_id": key, "root_id": root["root_id"], "arm": arm,
                    "input_tokens": len(body["token_ids"]), "prefix_sha256": fresh.digest(body["token_ids"])})
    assert len(tasks) == 12 and len(calls) == len(requests) == 72
    assert max(row["input_tokens"] + 384 for row in token_rows) <= 8192
    fresh.write_x(ROOT / "TOKEN_PREFLIGHT.json", {"rows": token_rows,
        "all_prefix_plus_output_le8192": True, "token_lengths_not_matched": True})
    fresh.write_x(ROOT / "PUBLIC_ROOTS.json", {"roots": roots,
        "generation_seeds": list(range(202609400000, 202609400012)),
        "no_prior_root_or_candidate_id_overlap": True, "prior_manifests": [str(path) for path in previous]})
    fresh.write_x(ROOT / "PUBLIC_INPUTS.json", {"schema": "b05-state-representation72-plan-v1",
        "tasks": tasks, "calls": calls, "prompts": prompts, "requests": requests,
        "host_labels_accessed_before_public_freeze": False})
    host = []
    for task, child in zip(tasks, children, strict=True):
        answer = api.solve_child_reference(child); assert answer == api.solve_child_independent(child)
        host.append({"root_id": task["root_id"],
                     "gold_ids": [row["implementation_id"] for row in answer["rows"]]})
    fresh.write_x(ROOT / "HOST_GOLD.json", {"rows": host,
        "labels_computed_after_public_freeze": True, "two_independent_solvers_agree": True})
    (ROOT / "HOST_GOLD.json").chmod(0o600)
    fresh.write_x(ROOT / "DATA_READY.json", {"schema": "b05-state-representation-data-ready-v1",
        "tasks": 12, "paired_seed_units": 24, "planned_calls": 72,
        "generation_seed_range": [202609400000, 202609400011],
        "decode_seed_range": [202609410000, 202609410023], "arms": ["raw","unresolved","resolved"],
        "represent_sha256": fresh.sha(ROOT / "represent.py"),
        "normalizer_sha256": fresh.sha(NORMALIZE), "public_inputs_sha256": fresh.sha(ROOT / "PUBLIC_INPUTS.json"),
        "host_gold_sha256": fresh.sha(ROOT / "HOST_GOLD.json"), "GPU_calls": 0, "model_calls": 0})
    print(json.dumps(fresh.read(ROOT / "DATA_READY.json"), sort_keys=True))


if __name__ == "__main__":
    main()
