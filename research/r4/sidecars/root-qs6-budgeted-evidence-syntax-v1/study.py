"""Fresh paired screen of zero-shot versus one syntax-only budgeted-interface example."""

import copy
from collections import Counter
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE = SIDE / "root-qs6-budgeted-evidence-stop-v1"
RECOVERY = SIDE / "root-record-map-batch-handoff-v1"
ALLOCATION_RUNTIME = SIDE / "runtime-an22-5801-v1"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
ATTEMPT = ROOT / "outputs/attempt-001"
PREFIX_INPUT = ROOT / "PREFIXES.json"
TASK_INPUT = ROOT / "TASKS.json"
ARMS = ("budgeted_plain", "budgeted_syntax_example")
SEED_BASE = 202609123000
PHASE_PREFIX = "qs6-budgeted-evidence-syntax-v1"
OUTER_SECONDS = 1100
ARM_SECONDS = 420
SOURCE_PROTOCOL_SHA256 = "a04479698744837f003518a6ec36b35cd29be25df8f1ea03a55f9c40b36e81bb"
SOURCE_STUDY_SHA256 = "2a3c6991ee41bc73c86438f3f1fa4fcfe0b204ccc1dd50629ec863f16afb0480"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha_text(value):
    return hashlib.sha256(value.encode()).hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def _load_source_study():
    if sha(SOURCE / "protocol.py") != SOURCE_PROTOCOL_SHA256:
        raise ValueError("source protocol changed")
    if sha(SOURCE / "study.py") != SOURCE_STUDY_SHA256:
        raise ValueError("source study changed")
    protocol_spec = importlib.util.spec_from_file_location(
        "syntax_screen_source_protocol", SOURCE / "protocol.py"
    )
    protocol = importlib.util.module_from_spec(protocol_spec)
    protocol_spec.loader.exec_module(protocol)
    previous = sys.modules.get("protocol")
    sys.modules["protocol"] = protocol
    try:
        spec = importlib.util.spec_from_file_location(
            "syntax_screen_source_study", SOURCE / "study.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop("protocol", None)
        else:
            sys.modules["protocol"] = previous
    return module


BASE = _load_source_study()


def runtime():
    return BASE.runtime()


@functools.lru_cache(maxsize=1)
def terminal_study():
    value = BASE.terminal_study()
    value.runtime = runtime
    value.qs.runtime = runtime
    return value


def data():
    return BASE.data()


def maps():
    return BASE.maps()


def saved_map(row):
    return BASE.saved_map(row)


def binding():
    return BASE.binding()


information_access_audit = BASE.information_access_audit


def phase(condition):
    if condition not in ARMS:
        raise ValueError("unknown syntax condition")
    return f"{PHASE_PREFIX}-{condition}"


def make_plan(condition):
    if condition not in ARMS:
        raise ValueError("unknown syntax condition")
    result = []
    for pair_index, original in enumerate(BASE.make_plan("budgeted_as_needed")):
        row = copy.deepcopy(original)
        row.update(
            namespace=phase(condition),
            syntax_condition=condition,
            interface_arm=condition,
            seed=SEED_BASE + pair_index,
        )
        row.pop("id", None)
        row["pair_id"] = digest(
            {
                "task_name": row["task_name"],
                "source_context_id": row["source_context_id"],
                "helper_repeat": row["repeat"],
                "seed": row["seed"],
            }
        )
        row["id"] = digest(row)
        result.append(row)
    if len(result) != 24 or len({row["id"] for row in result}) != 24:
        raise ValueError("syntax arm is not exact 24-coordinate inventory")
    if Counter(row["family"] for row in result) != Counter(
        {name: 4 for name in BASE.SOURCE_STUDY.FAMILIES}
    ):
        raise ValueError("syntax arm family balance changed")
    return result


SYNTAX_EXAMPLE = (
    "Toy syntax illustration only, using placeholder variables that are not actual record IDs: "
    "`chosen_ids = [record_id_you_selected]; returned_labels = classify(chosen_ids); "
    "computed_integer = your_task_specific_computation; "
    "finish(computed_integer, chosen_ids)`, followed after the Python action by "
    "`Answer: <the same computed integer>`. Replace every placeholder from the actual task state. "
    "This illustration does not tell you which records to select, what labels will be returned, "
    "how to compute the task operator, what answer to use, or when to stop. "
)


def _source_row(row):
    value = dict(row)
    value["interface_arm"] = "budgeted_as_needed"
    return value


def root_prompt(context, row):
    prompt = BASE.root_prompt(context, _source_row(row))
    if row["syntax_condition"] == "budgeted_plain":
        return prompt
    if row["syntax_condition"] != "budgeted_syntax_example":
        raise ValueError("unknown syntax condition")
    marker = "query.txt contains the exact question below."
    if prompt.count(marker) != 1:
        raise ValueError("source query marker changed")
    return prompt.replace(marker, SYNTAX_EXAMPLE + marker)


def make_task(context, row, gold):
    task = BASE.make_task(context, _source_row(row), gold)
    finalize0 = task.finalize

    async def finalize(trace, runtime):
        await finalize0(trace, runtime)
        if trace is not None and "budgeted_evidence" in trace.info:
            trace.info["budgeted_evidence"]["syntax_condition"] = row["syntax_condition"]

    task.finalize = finalize
    task.data = task.data.model_copy(
        update={
            "prompt": root_prompt(context, row),
            "source_split": "research-exposed-qs6-budgeted-syntax-screen",
        }
    )
    task.syntax_condition = row["syntax_condition"]
    task.coordinate_id = row["id"]
    return task


def no_child_system():
    return BASE.no_child_system()


def build_prefixes():
    native = terminal_study().qs.qnative().stack().native
    renderer = native.renderer()
    tools = json.loads(read(BASE.SOURCE_INPUTS / "NATIVE_TEMPLATE.json")["tools_ordered_json"])
    public = {row["id"]: row for row in data()[0]}
    rows = {}
    for condition in ARMS:
        for row in make_plan(condition):
            prompt = root_prompt(public[row["context_id"]], row)
            token_ids = renderer.render(
                [
                    {"role": "system", "content": no_child_system()},
                    {"role": "user", "content": prompt},
                ],
                tools=tools,
                add_generation_prompt=True,
            ).token_ids
            rows[row["id"]] = {
                "token_ids": token_ids,
                "token_sha256": digest(token_ids),
                "token_count": len(token_ids),
                "prompt_sha256": sha_text(prompt),
                "syntax_condition": condition,
            }
    return rows


@functools.lru_cache(maxsize=1)
def prefixes():
    return read(PREFIX_INPUT)


def verify():
    ready = read(ROOT / "READY.json")
    if ready["identity"] != digest({key: value for key, value in ready.items() if key != "identity"}):
        raise ValueError("syntax-screen READY identity changed")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("syntax-screen closure changed: " + path)
    for condition in ARMS:
        if ready["plan_ids"][condition] != [row["id"] for row in make_plan(condition)]:
            raise ValueError("syntax-screen plan changed")
    return ready
