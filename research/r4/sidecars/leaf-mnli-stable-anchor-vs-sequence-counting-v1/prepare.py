"""CPU-only inventory freeze, input generation, qualification, and seal."""

import copy
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import time

import protocol as p
import study as s


PARQUET = Path(
    "/project/alex_phd/research-cache/datasets/"
    "multinli-correspondence-feasibility-20260909-da70db2/validation_matched.parquet"
)
PARQUET_SHA = "350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186"
CACHE = PARQUET.parent


def loader():
    return s.load(
        "stable_anchor_inventory_loader",
        s.LOADER / "prepare.py",
        "7f0958b789af8969264d6fe8aa08b4f383c784a81232def78e5ae9a002fe575d",
        {"study": s, "protocol": p},
    )


def freeze(path, value):
    if path.exists():
        if s.read(path) != value:
            raise ValueError("frozen artifact differs: " + str(path))
    else:
        s.write(path, value)


def inventory():
    if s.sha(PARQUET) != PARQUET_SHA:
        raise ValueError("source parquet changed")
    helper = loader()
    paths, excluded, premise_groups = helper.named_inventory()
    value = {
        "schema": "mnli-inventory-before-selection-v1",
        "created_epoch": time.time(),
        "master": p.MASTER,
        "scope": "all named MNLI DATA/PUBLIC/GROUPS/PLAN inventories existing before selection",
        "paths": [str(path) for path in paths],
        "sha256": {str(path): s.sha(path) for path in paths},
        "excluded_normalized_hashes": sorted(excluded),
        "excluded_premise_groups": sorted(premise_groups),
        "source_parquet_sha256": s.sha(PARQUET),
    }
    freeze(s.ROOT / "INVENTORY_SNAPSHOT.json", value)
    print({"paths": len(paths), "excluded": len(excluded), "groups": len(premise_groups)})


def typed_prompt(tokenizer, body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest

    value = ChatCompletionRequest.model_validate(copy.deepcopy(body))
    if value.tools:
        raise ValueError("tools prohibited")
    return tokenizer.apply_chat_template(
        body["messages"],
        tools=None,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=False,
        **value.chat_template_kwargs,
    )


def named_ids(paths):
    pattern = re.compile(r'"(m[0-9a-f]{12})"')
    values = set()
    for path in paths:
        values.update(pattern.findall(Path(path).read_text(errors="replace")))
    return values


def make_aliens(contexts, tokenizer, occupied):
    result = {}
    for context in contexts:
        values = []
        for position, target in enumerate(p.requested_tags(context)):
            wanted = len(tokenizer.encode(target, add_special_tokens=False))
            nonce = 0
            while True:
                candidate = "m" + hashlib.sha256(
                    f"stable-anchor:{p.MASTER}:{context['index']}:{position}:{nonce}".encode()
                ).hexdigest()[:12]
                if candidate not in occupied and len(
                    tokenizer.encode(candidate, add_special_tokens=False)
                ) == wanted:
                    break
                nonce += 1
            occupied.add(candidate)
            values.append(candidate)
        result[str(context["index"])] = values
    return result


def seed_scan():
    needles = {str(seed) for seed in p.SEEDS}
    matches = []
    paths = set(s.SIDE.glob("*/*.json")) | set(s.SIDE.glob("*/inputs/*.json"))
    for path in sorted(paths):
        if s.ROOT in path.parents:
            continue
        found = sorted(needles & set(re.findall(r"\b\d{9}\b", path.read_text(errors="replace"))))
        if found:
            matches.append({"path": str(path), "seeds": found})
    return {"scope": "named non-output sidecar JSON before seal", "matches": matches}


def inputs():
    import pyarrow.parquet as pq
    import xgrammar as xg

    snapshot = s.read(s.ROOT / "INVENTORY_SNAPSHOT.json")
    if snapshot["master"] != p.MASTER or snapshot["source_parquet_sha256"] != s.sha(PARQUET):
        raise ValueError("inventory/source mismatch")
    for path, pin in snapshot["sha256"].items():
        if s.sha(path) != pin:
            raise ValueError("inventory changed after freeze: " + path)
    helper = loader()
    rows = pq.read_table(PARQUET).to_pylist()
    excluded = set(snapshot["excluded_normalized_hashes"])
    prior_groups = set(snapshot["excluded_premise_groups"])
    contexts, counts, conflicts, ranked = helper.select(rows, excluded)
    if contexts is None:
        freeze(
            s.ROOT / "INSUFFICIENT_POOL.json",
            {
                "eligible_by_genre": counts,
                "required_by_genre": 64,
                "inventory_snapshot_sha256": s.sha(s.ROOT / "INVENTORY_SNAPSHOT.json"),
                "preserved": True,
            },
        )
        raise ValueError("insufficient eligible pool")
    rotated = [
        {**row, "label": (row["label"] + 1) % 3 if row["label"] in (0, 1, 2) else row["label"]}
        for row in rows
    ]
    changed, _, _, changed_ranked = helper.select(rotated, excluded)
    invariant = (
        changed is not None
        and helper.public(changed) == helper.public(contexts)
        and ranked == changed_ranked
    )
    selected = {group for context in contexts for group in context["premise_groups"]}
    overlap = sorted(selected & prior_groups)
    if not invariant or overlap or conflicts:
        raise ValueError("selection invariant")

    tokenizer = s.tokenizer()
    occupied = named_ids(snapshot["paths"])
    occupied.update(record["id"] for context in contexts for record in context["records"])
    aliens = make_aliens(contexts, tokenizer, occupied)
    opaque = {value for context in contexts for value in p.anchor_values(context, "opaque")}
    all_m_ids = occupied | {value for values in aliens.values() for value in values}
    if opaque & all_m_ids or any(not value.startswith("k") for value in opaque):
        raise ValueError("stable key names a source/reference ID")

    freeze(s.ROOT / "DATA.json", {"contexts": contexts})
    freeze(s.ROOT / "PUBLIC.json", helper.public(contexts))
    freeze(s.ROOT / "ALIEN_DICTIONARIES.json", aliens)
    plan = p.plan()
    requests = {
        row["id"]: p.request(contexts[row["context_index"]], row, aliens[str(row["context_index"])])
        for row in plan
    }
    wires = {key: s.serialize(value) for key, value in requests.items()}
    prompts = {key: typed_prompt(tokenizer, value) for key, value in requests.items()}
    config = s.read(Path(s.MODEL["path"]) / "config.json")
    vocabulary = config.get("text_config", config)["vocab_size"]
    compiler = xg.GrammarCompiler(
        xg.TokenizerInfo.from_huggingface(tokenizer, vocab_size=vocabulary),
        max_threads=2,
        cache_enabled=True,
    )
    checks = []
    for row in plan:
        context = contexts[row["context_index"]]
        body = requests[row["id"]]
        grammar = compiler.compile_json_schema(
            s.serialize(body["structured_outputs"]["json"]), any_whitespace=True
        )
        matcher = xg.GrammarMatcher(grammar)
        if row["anchor"] == "labels_only":
            good = ["neutral"] * 48
            key_tokens = []
        else:
            keys = p.anchor_values(context, row["anchor"])
            good = [{"key": key, "label": "neutral"} for key in keys]
            key_tokens = [len(tokenizer.encode(str(key), add_special_tokens=False)) for key in keys]
        if not matcher.accept_string(s.serialize(good).encode()) or not matcher.is_completed():
            raise ValueError("grammar rejects canonical output")
        if len(prompts[row["id"]]) + 3072 > 8192:
            raise ValueError("native context overflow")
        checks.append(
            {
                "id": row["id"],
                "arm": row["arm"],
                "prompt_tokens": len(prompts[row["id"]]),
                "key_token_lengths": key_tokens,
                "canonical_contract_accepts": True,
            }
        )
    scan = seed_scan()
    if scan["matches"]:
        raise ValueError("seed collision")
    selection = {
        "master": p.MASTER,
        "source_rows": len(rows),
        "inventory_snapshot_sha256": s.sha(s.ROOT / "INVENTORY_SNAPSHOT.json"),
        "eligible_by_genre": counts,
        "selected_contexts": 16,
        "selected_premise_groups": 256,
        "prior_selected_overlap": overlap,
        "first_64_ranked_groups_per_genre": ranked,
        "eligibility_uses_labels": True,
        "eligibility_rule": "exactly three conflict-free deduplicated pairs with labels {0,1,2}",
        "ranking_uses_labels_gold_length_or_outcomes": False,
        "label_mutation_ranking_invariant": invariant,
        "scope": "named-inventory excluded; not globally or pretraining unseen",
    }
    manifest = {
        "dataset": "nyu-mll/multi_nli",
        "revision": "da70db2af9d09693783c3320c4249840212ee221",
        "split": "validation_matched",
        "license": "Mixed OANC permissive terms / CC-BY-3.0 / CC-BY-SA-3.0 / public-domain fiction; see pinned card",
        "parquet_sha256": s.sha(PARQUET),
        "readme_sha256": s.sha(CACHE / "README.md"),
        "acquisition_sha256": s.sha(CACHE / "ACQUISITION.json"),
        "retrieved_utc": s.read(CACHE / "ACQUISITION.json")["retrieved_utc"],
    }
    artifacts = {
        "PLAN.json": plan,
        "REQUESTS.json": requests,
        "ORDERED_REQUESTS.json": wires,
        "PROMPT_IDS.json": prompts,
        "CPU_NATIVE.json": {
            "requests": 192,
            "schemas_compiled": 192,
            "checks": checks,
            "max_prompt_tokens": max(map(len, prompts.values())),
            "max_prompt_plus_output": max(map(len, prompts.values())) + 3072,
            "request_wire_sha256": {
                key: hashlib.sha256(value.encode()).hexdigest() for key, value in wires.items()
            },
            "versions": {
                name: importlib.metadata.version(name)
                for name in ("vllm", "transformers", "xgrammar")
            },
            "gpu_calls": 0,
            "service_calls": 0,
        },
        "PLANNED_NULL_ENDPOINTS.json": [p.null_row(row, "not attempted") for row in plan],
        "SELECTION_AUDIT.json": selection,
        "SEED_SCAN.json": scan,
        "DATASET_MANIFEST.json": manifest,
    }
    for name, value in artifacts.items():
        freeze(s.ROOT / name, value)
    print({"contexts": 16, "requests": 192, "eligible": counts, "max_prompt": max(map(len, prompts.values()))})


def qualify():
    command = [str(s.NATIVE), "-m", "pytest", "-q", "test_protocol.py", "test_science.py", "test_runtime.py"]
    started = time.time()
    result = subprocess.run(
        command,
        cwd=s.ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    freeze(
        s.ROOT / "CPU_TESTS.json",
        {
            "argv": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "elapsed_seconds": time.time() - started,
            "source_sha256": {str(path): s.sha(path) for path in s.ROOT.glob("*.py")},
            "gpu_calls": 0,
            "service_calls": 0,
        },
    )
    print(result.stdout, result.stderr)
    if result.returncode:
        raise SystemExit(result.returncode)


def seal():
    tests = s.read(s.ROOT / "CPU_TESTS.json")
    if tests["returncode"] != 0:
        raise ValueError("qualification failed")
    for path, pin in tests["source_sha256"].items():
        if s.sha(path) != pin:
            raise ValueError("source changed after tests: " + path)
    input_names = (
        "INVENTORY_SNAPSHOT.json", "DATA.json", "PUBLIC.json", "ALIEN_DICTIONARIES.json",
        "PLAN.json", "REQUESTS.json", "ORDERED_REQUESTS.json", "PROMPT_IDS.json",
        "CPU_NATIVE.json", "PLANNED_NULL_ENDPOINTS.json", "SELECTION_AUDIT.json",
        "SEED_SCAN.json", "DATASET_MANIFEST.json",
    )
    inputs_sha = {str(s.ROOT / name): s.sha(s.ROOT / name) for name in input_names}
    sources_sha = {
        str(path): s.sha(path)
        for path in s.ROOT.iterdir()
        if path.is_file() and path != s.READY_PATH
    }
    sources_sha[str(s.PRIOR / "READY.json")] = s.sha(s.PRIOR / "READY.json")
    ready = {
        "schema": "leaf-mnli-stable-anchor-vs-sequence-counting-ready-v1",
        "status": "CPU_READY_FOR_MAIN_ACCEPTANCE",
        "planned_endpoints": 192,
        "contexts": 16,
        "arms": list(p.ARMS),
        "primary_descriptive": "late pooled stable-key gain minus sequential gain",
        "opaque_gate": {
            "own_gain_pp": 25,
            "within_sequential_pp": 10,
            "positive_contexts": 12,
            "minimum_available_each_cell": 15,
            "no_contract_or_availability_disadvantage": True,
        },
        "numeric_gate_reported_separately": True,
        "model": s.MODEL,
        "adapter": None,
        "seeds": list(p.SEEDS),
        "workers": 4,
        "request_seconds": 90,
        "outer_seconds": 1800,
        "work_seconds": 1650,
        "owned_seconds": 1770,
        "argv": [str(s.NATIVE), str(s.ROOT / "owner.py"), "run", "--output", str(s.ATTEMPT)],
        "source_sha256": sources_sha,
        "input_sha256": inputs_sha,
        "gpu_calls": 0,
        "service_calls": 0,
    }
    ready["identity"] = s.digest(ready)
    s.write(s.READY_PATH, ready)
    s.verify()
    print({"ready_sha256": s.sha(s.READY_PATH), "identity": ready["identity"]})


if __name__ == "__main__":
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("command", choices=("inventory", "inputs", "qualify", "seal"))
    args = parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU only: set CUDA_VISIBLE_DEVICES to empty")
    globals()[args.command]()
