"""CPU-only immutable input preparation and READY seal."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import unicodedata

import protocol as p
import study as s

PARQUET = Path("/project/alex_phd/research-cache/datasets/multinli-correspondence-feasibility-20260909-da70db2/validation_matched.parquet")
PARQUET_SHA = "350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186"
FIELD = s.SIDE / "leaf-mnli-field-order-replication-v1"


def norm(text): return " ".join(unicodedata.normalize("NFKC", text).casefold().split())
def group(text): return hashlib.sha256(norm(text).encode()).hexdigest()
def pair(row): return p.digest([norm(row["premise"]), norm(row["hypothesis"])])


def helper():
    return s.load("downstream_inventory", FIELD / "prepare.py",
        "7f0958b789af8969264d6fe8aa08b4f383c784a81232def78e5ae9a002fe575d",
        {"study": s.stable, "protocol": p})


def typed(tokenizer, body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    value = ChatCompletionRequest.model_validate(copy.deepcopy(body))
    return tokenizer.apply_chat_template(body["messages"], tools=None, add_generation_prompt=True,
        tokenize=True, return_dict=False, **value.chat_template_kwargs)


def select(rows, excluded):
    eligible, conflicts = helper().eligible_groups(rows, excluded)
    contexts = []; receipt = {}
    for genre in p.GENRES:
        ranked = sorted((key for key, vals in eligible.items() if vals[0][2]["genre"] == genre),
            key=lambda key: p.digest([p.MASTER, "select", genre, key]))
        receipt[genre] = {"eligible": len(ranked), "first96": ranked[:96]}
        if len(ranked) < 96: return None, receipt, conflicts
        for block in range(2):
            records = []
            for key in ranked[block * 48:(block + 1) * 48]:
                values = eligible[key]
                chosen = min(values, key=lambda value: p.digest([p.MASTER, "row", key, value[0]]))
                pair_id, source_row, row = chosen
                identifier = "r" + pair_id[:12]
                user = p.USERS[int(p.digest([p.MASTER, "user", identifier])[:8], 16) % 4]
                weight = 1 + int(p.digest([p.MASTER, "weight", identifier])[:8], 16) % 9
                records.append({"id": identifier, "premise": row["premise"], "hypothesis": row["hypothesis"],
                    "gold_label": p.LABELS[row["label"]], "user": user, "weight": weight,
                    "premise_group": key, "pair_group": pair_id, "source_row": source_row})
            index = len(contexts)
            records.sort(key=lambda row: p.digest([p.MASTER, "display", index, row["id"]]))
            questions = []
            for qi, operator in enumerate(("count", "weight")):
                relation = p.LABELS[int(p.digest([p.MASTER, "relation", index, qi])[:8], 16) % 3]
                order = sorted(p.USERS, key=lambda user: p.digest([p.MASTER, "users", index, qi, user]))
                take = 1 + int(p.digest([p.MASTER, "take", index, qi])[:8], 16) % 3
                questions.append({"operator": operator, "relation": relation, "users": sorted(order[:take])})
            contexts.append({"id": f"bridge-{genre}-{block}", "index": index, "genre": genre,
                "premise_groups": ranked[block * 48:(block + 1) * 48], "records": records, "questions": questions})
    return contexts, receipt, conflicts


def inputs():
    import pyarrow.parquet as pq
    if s.sha(PARQUET) != PARQUET_SHA: raise ValueError("source parquet changed")
    paths, excluded, prior = helper().named_inventory()
    rows = pq.read_table(PARQUET).to_pylist(); contexts, receipt, conflicts = select(rows, excluded)
    inventory = {"created_epoch": time.time(), "scope": "all named MNLI DATA/PUBLIC/GROUPS/PLAN before selection",
        "paths": [str(path) for path in paths], "sha256": {str(path): s.sha(path) for path in paths},
        "excluded_premise_groups": sorted(prior), "excluded_normalized_hashes": sorted(excluded),
        "source_parquet_sha256": s.sha(PARQUET)}
    if (s.ROOT / "INVENTORY_SNAPSHOT.json").exists():
        prior_inventory = s.read(s.ROOT / "INVENTORY_SNAPSHOT.json")
        if {k: prior_inventory[k] for k in inventory if k != "created_epoch"} != {k: inventory[k] for k in inventory if k != "created_epoch"}:
            raise ValueError("preserved inventory differs")
    else:
        s.write(s.ROOT / "INVENTORY_SNAPSHOT.json", inventory)
    if contexts is None:
        s.write(s.ROOT / "INSUFFICIENT_POOL.json", {"required_per_genre": 96, "receipt": receipt, "preserved": True}); raise ValueError("insufficient pool")
    answers = {op: [] for op in ("count", "weight")}
    for context in contexts:
        labels = {row["id"]: row["gold_label"] for row in context["records"]}
        for question in context["questions"]: answers[question["operator"]].append(p.reduce_answer(context, labels, question))
    varied = {op: {"answers": values, "distinct": len(set(values)), "max_frequency": max(values.count(v) for v in set(values)), "zeros": values.count(0)} for op, values in answers.items()}
    if any(v["distinct"] < 4 or v["max_frequency"] > 4 or v["zeros"] > 2 for v in varied.values()):
        s.write(s.ROOT / "VARIED_GOLD_INSUFFICIENT.json", {"gate": varied, "preserved": True}); raise ValueError("fixed varied-gold gate failed")
    public = [{**{k: c[k] for k in ("id", "index", "genre", "premise_groups", "questions")},
        "size": 48, "stratum": "new_inventory_weighted_mnli", "native_context_id": 31000 + c["index"],
        "text": "\n".join(json.dumps({"id": row["id"], "user": row["user"], "text": "Premise: " + row["premise"] + " Hypothesis: " + row["hypothesis"], "weight": row["weight"]}, separators=(",", ":")) for row in c["records"]),
        "records": [{"id": row["id"], "user": row["user"], "text": "Premise: " + row["premise"] + " Hypothesis: " + row["hypothesis"], "weight": row["weight"]} for row in c["records"]]} for c in contexts]
    gold = {c["id"]: {"labels": {r["id"]: r["gold_label"] for r in c["records"]},
        "answers": {str(i): p.reduce_answer(c, {r["id"]: r["gold_label"] for r in c["records"]}, q) for i, q in enumerate(c["questions"])}} for c in contexts}
    plan = p.root_plan(public); child = s.binding()["fixed_child"]
    leaf = {encoding: {c["id"]: p.leaf_request(c, encoding, child) for c in contexts} for encoding in p.ENCODINGS}
    tokenizer = s.stable.tokenizer(); leaf_prompts = {e: {cid: typed(tokenizer, body) for cid, body in vals.items()} for e, vals in leaf.items()}
    dummy = {row["id"]: "neutral" for row in public[0]["records"]}
    prompts = {}
    for row in plan:
        context = next(c for c in public if c["id"] == row["context_id"])
        task = s.make_task(context, row, gold[context["id"]]["answers"][str(row["query_index"])], dummy)
        prompts[row["id"]] = s.qnative.first_prefix(task)
    tasks = {row["id"]: {"prompt": p.root_prompt(next(c for c in public if c["id"] == row["context_id"]), row)} for row in plan}
    template = s.read(s.scale.ORIGINAL / "inputs/NATIVE_TEMPLATE.json")
    artifacts = {"DATA.json": {"contexts": contexts}, "PUBLIC.json": public, "HOST_GOLD.json": gold,
        "ROOT_PLAN.json": plan, "FREE_PLAN.json": plan, "TASKS.json": tasks,
        "LEAF_REQUESTS.json": leaf, "LEAF_PROMPT_IDS.json": leaf_prompts,
        "PROMPTS_ACCURATE.json": prompts, "NATIVE_TEMPLATE.json": template,
        "PLANNED_NULL_ENDPOINTS.json": {"leaf": 16, "root": 64},
        "SELECTION_AUDIT.json": {"master": p.MASTER, "receipt": receipt, "varied_gold": varied,
            "panel_sha256": p.digest(contexts), "eligibility_amendment": "max frequency 3 to 4 before model output",
            "strongest_constant_answer_baseline": {"operator": "count", "value": 3, "correct": 4, "planned": 8},
            "pair_conflicts": conflicts, "selected_groups": 384, "eligibility_uses_gold": True,
            "ranking_or_row_choice_uses_gold_length_outcomes": False, "prior_overlap": []},
        "DATASET_MANIFEST.json": {"dataset": "nyu-mll/multi_nli", "revision": "da70db2af9d09693783c3320c4249840212ee221",
            "split": "validation_matched", "parquet_sha256": PARQUET_SHA,
            "license": "mixed OANC permissive / CC-BY-3.0 / CC-BY-SA-3.0 / public-domain; pinned source card"}}
    s.INPUTS.mkdir()
    for name, value in artifacts.items(): s.write(s.INPUTS / name, value)


def qualify():
    command = [str(s.NATIVE), "-m", "pytest", "-q", "test_protocol.py", "test_runtime.py"]
    started = time.time(); result = subprocess.run(command, cwd=s.ROOT, capture_output=True, text=True, timeout=300,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"})
    s.write(s.ROOT / "CPU_TESTS.json", {"argv": command, "returncode": result.returncode, "stdout": result.stdout,
        "stderr": result.stderr, "elapsed_seconds": time.time() - started,
        "source_sha256": {str(path): s.sha(path) for path in s.ROOT.glob("*.py")}, "gpu_calls": 0, "service_calls": 0})
    print(result.stdout); print(result.stderr)
    if result.returncode: raise SystemExit(result.returncode)


def seal():
    tests = s.read(s.ROOT / "CPU_TESTS.json")
    if tests["returncode"] != 0: raise ValueError("focused tests failed")
    for path, pin in tests["source_sha256"].items():
        if s.sha(path) != pin: raise ValueError("source changed after qualification: " + path)
    inputs = {str(path): s.sha(path) for path in sorted(s.INPUTS.glob("*.json"))}
    sources = {str(path): s.sha(path) for path in sorted(s.ROOT.iterdir()) if path.is_file() and path.name != "READY.json"}
    sources[str(s.ANALYSIS / "FINAL_SEAL.json")] = s.sha(s.ANALYSIS / "FINAL_SEAL.json")
    sources[str(s.SCALE / "READY_v2.json")] = s.sha(s.SCALE / "READY_v2.json")
    audit = s.read(s.INPUTS / "SELECTION_AUDIT.json")
    ready = {"schema": "root-stable-anchor-downstream-bridge-ready-v1",
        "status": "CPU_READY_FOR_MAIN_ACCEPTANCE", "admitted_encoding": "opaque",
        "admission_rule": "opaque-first; both upstream gates passed",
        "upstream_final_seal_sha256": "f3923f17e472b4ca1051e2448c7175de21f844832c5a822a323b980730c99430",
        "planned_model_episodes_minimum": 80, "leaf_acquisitions": 16, "root_episodes": 64,
        "contexts": 8, "clustered_units": 8, "panel_sha256": audit["panel_sha256"],
        "eligibility_amendment": "max-frequency 3 to 4; exact panel retained pre-output",
        "count_constant_baseline": "4/8 at answer 3", "root_api": "classify_all canonical public map",
        "root_policies": ["supplied", "free"], "questions": ["count", "weight"],
        "master_seed": p.MASTER, "leaf_seeds": [998431101 + i for i in range(8)],
        "root_seed_rule": "998431301 + 10*context_index + query_index; shared across four cells",
        "binding": s.binding(), "binding_sha256": s.digest(s.binding()),
        "workers": 4, "request_seconds": 90, "leaf_output_tokens": 3072, "root_output_tokens": 2048,
        "outer_seconds": 1800, "owned_seconds": 1770, "work_seconds": 1650,
        "no_retry_refill_fallback": True, "argv": [str(s.NATIVE), str(s.ROOT / "owner.py"), "run", "--output", str(s.ATTEMPT)],
        "source_sha256": sources, "input_sha256": inputs, "gpu_calls": 0, "service_calls": 0,
        "prepared_epoch": time.time()}
    ready["identity"] = s.digest(ready); s.write(s.ROOT / "READY.json", ready); s.verify()
    print(json.dumps({"ready_sha256": s.sha(s.ROOT / "READY.json"), "identity": ready["identity"]}, sort_keys=True))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("inputs", "qualify", "seal")); args = parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU only")
    globals()[args.command]()
