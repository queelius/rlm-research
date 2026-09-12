"""Frozen six-family recursion-interface qualifier."""

import copy
import functools
import hashlib
import importlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
HEADROOM = SIDE / "root-qs6-recursion-headroom-v1"
SOURCE = SIDE / "root-question-sensitive-terminal-rlvr-lr1e5-v1"
SOURCE_INPUTS = SOURCE / "inputs"
REFERENCE = SIDE / "root-qs6-feedback-diagnostic-v1"
REFERENCE_SPEC = REFERENCE / "outputs/attempt-001/collection/CAPTURE_SPEC.json"
ALLOCATION_RUNTIME = SIDE / "runtime-an22-5801-v1"
RECOVERY = SIDE / "root-record-map-batch-handoff-v1"
NANO_RLM = Path(
    "/tmp/rlmc.an22-5801.ahAGos/root/vfs/dir/"
    "b50ce4f5b31918d4d2b15d21586825a9320f10fc20818b76f982bcd465d75efc/tmp/"
    "vf-rlm-4fa91253816bfa64435b7b727ec01bac2a7a7a2b72ece29ceb2474d26f95418d/checkout"
)
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
ATTEMPT = ROOT / "outputs/attempt-001"
OUTER_SECONDS = 700
OWNED_SECONDS = 600
ADMISSION_TRIGGER = 250
MODES = ("no_child", "enabled")
BLOCK_MODES = MODES
FAMILIES = ("J1", "J2", "M1", "M2", "T1", "T2")
SELECTION = {
    "J1": "question-sensitive-sft-protected-00",
    "J2": "question-sensitive-sft-protected-02",
    "M1": "question-sensitive-sft-protected-04",
    "M2": "question-sensitive-sft-protected-01",
    "T1": "question-sensitive-sft-protected-06",
    "T2": "question-sensitive-sft-protected-03",
}
SOURCE_SEEDS = {
    "J1": 2026091213,
    "J2": 2026091227,
    "M1": 2026091239,
    "M2": 2026091221,
    "T1": 2026091253,
    "T2": 2026091235,
}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


@functools.lru_cache(maxsize=1)
def public():
    return {row["id"]: row for row in read(SOURCE_INPUTS / "PUBLIC.json")}


def source_tasks():
    rows = read(SOURCE_INPUTS / "PLANS.json")["readout"]
    by_key = {(row["context_id"], row["family"]): row for row in rows}
    selected = [copy.deepcopy(by_key[(SELECTION[family], family)]) for family in FAMILIES]
    if [row["family"] for row in selected] != list(FAMILIES):
        raise ValueError("six-family source selection changed")
    if len({row["context_id"] for row in selected}) != 6:
        raise ValueError("qualifier must use six distinct context groups")
    return selected


def make_blocks():
    blocks = []
    for block_index, mode in enumerate(BLOCK_MODES):
        block = []
        for source in source_tasks():
            row = copy.deepcopy(source)
            pair = {
                "task_name": row["task_name"],
                "context_id": row["context_id"],
                "family": row["family"],
                "repeat": 0,
            }
            row.update(
                namespace="root-qs6-recursion-interface-qualifier-v1",
                mode=mode,
                repeat=0,
                seed=SOURCE_SEEDS[row["family"]],
                pair_id=digest(pair),
                source_plan_id=source["id"],
                source_headroom_seed=SOURCE_SEEDS[row["family"]],
                block_index=block_index,
                temperature=0.5,
                max_tokens=2048,
            )
            row.pop("id", None)
            row["id"] = digest(row)
            block.append(row)
        blocks.append(block)
    return blocks


def common_prompt(context, query):
    definitions = (
        "Classify the type of answer requested, not words mentioned in the question.\n"
        "human being: a person, an organization or group of people, or a person's role, title or description.\n"
        "location: a geographic place, including a city, country, state, mountain or other place.\n"
        "abbreviation: a shortened form, or the expanded wording represented by a shortened form.\n"
        "entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.\n"
        "description and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.\n"
        "numeric value: a quantity, count, measurement, date, duration, rank or numerical code.\n"
    )
    interface = (
        "Python and the task files are available. If the runtime system message advertises a "
        "callable `rlm`, it is already in your global namespace. Use exactly the interface "
        "`reply = await rlm(request_for(batch))`, then "
        "`labels = strict_map(reply.answer, [record[\"id\"] for record in batch])`; do not "
        "import `rlm` from any module. If the system "
        "message does not advertise `rlm`, recursive delegation is unavailable: do not import "
        "or call it, and solve from the raw files. batch_contract.py exposes request_for(batch) "
        "and strict_map(raw, ids): request_for includes exactly each record's ID and text while "
        "omitting user and weight; strict_map decodes a child response string and requires "
        "exactly the requested IDs and canonical categories. These helpers do not call a model, "
        "choose records, aggregate, check semantic correctness, or repair responses. A child "
        "label map is a prediction, not dataset truth. query.txt contains the exact question "
        "below. The final response must contain only Answer: N."
    )
    return (
        f'The files records.json (a JSON list) and context.txt (one JSON object per line) contain the same {context["size"]} public records, with exactly the fields id, user, text, and weight. '
        "id identifies a record; user is its public user identity; text is the original question; "
        "weight is a visible positive integer belonging to that record. Neither file contains "
        "category labels.\n\n" + definitions + "\n" + interface + "\n\nQuestion: " + query
    )


def environment(mode):
    if mode not in MODES:
        raise ValueError("unknown recursion mode")
    value = copy.deepcopy(read(REFERENCE_SPEC)["environment"])
    value["agent"]["harness"]["max_depth"] = 0 if mode == "no_child" else 1
    return value


def _systems():
    template = read(SOURCE_INPUTS / "NATIVE_TEMPLATE.json")["system"]
    enabled = template["content"]
    recursion = (
        "\n\nA callable `rlm` is already in your global namespace — call it directly with "
        "`await rlm('sub-task')` to spawn a recursive sub-agent. Returns an `RLMResult` with "
        "`.answer` (string), `.usage`, `.turns`, and `.session_dir`.\nFor parallel sub-agents, "
        "use normal Python async patterns such as `await asyncio.gather(rlm('task1'), "
        "rlm('task2'))`."
    )
    if enabled.count(recursion) != 1:
        raise ValueError("pinned nano-rlm recursion prompt seam changed")
    return {"enabled": enabled, "no_child": enabled.replace(recursion, "")}


def build_prefix_manifest():
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer

    base_path = read(SIDE / "root-adaptive-rlvr-v1/RECIPE.json")["base_model"]
    renderer = create_renderer(load_tokenizer(base_path), Qwen3RendererConfig(enable_thinking=True))
    template = read(SOURCE_INPUTS / "NATIVE_TEMPLATE.json")
    tools = json.loads(template["tools_ordered_json"])
    systems = _systems()
    coordinates = []
    for row in [item for block in make_blocks() for item in block]:
        prompt = common_prompt(public()[row["context_id"]], row["question"])
        messages = [
            {"role": "system", "content": systems[row["mode"]]},
            {"role": "user", "content": prompt},
        ]
        tokens = renderer.render(messages, tools=tools, add_generation_prompt=True).token_ids
        coordinates.append(
            {
                "id": row["id"],
                "mode": row["mode"],
                "task_name": row["task_name"],
                "token_ids": tokens,
                "token_count": len(tokens),
                "token_sha256": digest(tokens),
                "user_prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "system_advertises_rlm": "A callable `rlm`" in systems[row["mode"]],
            }
        )
    return {
        "schema": "root-qs6-recursion-interface-qualifier-prefixes-v1",
        "nano_rlm_commit": "4ef3438d55fdd39b18d34035833c73e13b006733",
        "nano_prompt_sha256": sha(NANO_RLM / "src/rlm/prompt.py"),
        "coordinates": coordinates,
    }


def runtime():
    for name in ("study_wrapper", "lifecycle_adapter", "credential_preflight", "service_wrapper"):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(ALLOCATION_RUNTIME))
    credential = importlib.import_module("credential_preflight")
    lifecycle = importlib.import_module("lifecycle_adapter")
    wrapper = importlib.import_module("study_wrapper")
    wrapper.verify_runtime()
    lifecycle.verify()
    credential.require_provider_credential()
    return wrapper, lifecycle


def _terminal_study():
    if str(SOURCE) not in sys.path:
        sys.path.insert(0, str(SOURCE))
    terminal = importlib.import_module("terminal_study")
    terminal.runtime = runtime
    terminal.qs.runtime = runtime
    return terminal


def verify():
    ready = read(ROOT / "READY.json")
    if ready["identity"] != digest({key: value for key, value in ready.items() if key != "identity"}):
        raise ValueError("READY identity mismatch")
    for path, pin in ready["closure_sha256"].items():
        if sha(path) != pin:
            raise ValueError("frozen qualifier closure changed: " + path)
    if ready["plan_ids"] != [[row["id"] for row in block] for block in make_blocks()]:
        raise ValueError("frozen plan changed")
    return ready
