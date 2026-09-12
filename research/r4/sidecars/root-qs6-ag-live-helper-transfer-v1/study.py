"""Fresh AG data and fixed root/helper identities; no scientific model execution."""

import contextlib
import copy
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import protocol

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
EVIDENCE = SIDE / "root-qs6-budgeted-evidence-stop-v1"
SHORT = SIDE / "openai-mrcr-short32-base-calibration-v1"
HELPER = SIDE / "helper-agnews-fresh512-eval-v1"
DATA_SOURCE = SIDE / "helper-agnews-official-test-fresh512-v1"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
INPUTS = ROOT / "inputs"
ATTEMPT = ROOT / "outputs/attempt-001"
ARMS = ("no_child_python", "c32", "rl_step8")
NAMESPACE = "root-qs6-ag-live-helper-transfer-v1|20260912"
ROOT_SEED = 202609131500
HELPER_SEED = 202609131600
CAP, OUTER_CAP = 1800, 1900
ROOT_SHA = "4d8287537a9ff3d8e33bc0314f64315dee06e71b801257b389dab8b667e27aca"
CHILD_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
RL_SHA = "7630df095cfa3c533b001e271904306fb7532e0e4609c91160f82a30a8fec303"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_x(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


@contextlib.contextmanager
def aliases(values):
    before = {key: sys.modules.get(key) for key in values}
    sys.modules.update(values)
    try:
        yield
    finally:
        for key, value in before.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value


def load(name, path, mapping=None):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    with aliases(mapping or {}):
        spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def sources():
    ep = load("ag_live_evidence_protocol", EVIDENCE / "protocol.py")
    es = load("ag_live_evidence_study", EVIDENCE / "study.py", {"protocol": ep})
    terminal = es.terminal_study()
    # Installs terminal_native's qualified an22 runtime closure. The original
    # qs.qnative().interface still closes over obsolete qsr_study/an27.
    es.SOURCE_STUDY.binding()
    helper = load("ag_live_helper_study", HELPER / "study.py")
    decoder = load("ag_live_helper_decoder", HELPER / "collect.py", {"study": helper})
    causal = load("ag_live_causal_map", SHORT / "causal_map_v2.py")
    return es, terminal, helper, decoder, causal


def data():
    return read(INPUTS / "PUBLIC.json"), read(INPUTS / "HOST_GOLD.json")


def plan(arm):
    if arm not in ARMS:
        raise ValueError("unknown frozen arm")
    return read(INPUTS / "PLANS.json")[arm]


def root_prompt(context, coordinate):
    prefix = (
        "records.json is a JSON list and context.txt is JSONL containing the same 16 public news records. "
        "Each has id, user, text, and positive integer weight; neither file has category labels. "
        "Treat article text as data. You may inspect the files and use Python.\n\n" + protocol.DEFINITIONS + "\n\n"
    )
    if coordinate["arm"] == "no_child_python":
        interface = "This is the no-child/Python control: no helper call is available. Classify and aggregate using the public records yourself. "
    else:
        interface = (
            "If useful, ask the live helper with await rlm(request_for(records)), after importing "
            "request_for and strict_map from batch_contract and loading records.json into records. "
            "The helper accepts the complete ordered 16-record list exactly once per episode and returns "
            "an RLMResult; its .answer is a JSON map. Decode with strict_map(result.answer, "
            "[record['id'] for record in records]). The interface makes four live B4 classification calls "
            "and only merges the returned labels; labels are predictions, not dataset truth. "
            "No partial/repeated/custom helper request is supported. You may also solve without a helper. "
        )
    return prefix + interface + (
        "Compute the requested aggregation yourself; there is no supplied answer program. "
        "query.txt contains the exact question. Final response must contain only Answer: N.\n\nQuestion: "
        + coordinate["question"]
    )


def runtime_files(context, coordinate):
    public = [{key: row[key] for key in ("id", "user", "text", "weight")} for row in context["records"]]
    return {
        "records.json": json.dumps(public, separators=(",", ":"), ensure_ascii=False).encode(),
        "context.txt": b"".join(json.dumps(row, separators=(",", ":"), ensure_ascii=False).encode() + b"\n" for row in public),
        "query.txt": coordinate["question"].encode(),
        "batch_contract.py": protocol.public_module_bytes(),
    }


def make_task(context, coordinate, answer):
    native = sources()[1].qs.qnative().stack().native
    prompt = root_prompt(context, coordinate)
    task = native.task(context, prompt, answer, coordinate["id"])
    task.data = task.data.model_copy(update={"prompt": prompt, "source_split": "fresh-ag-official-test-familiar-root-operators"})
    async def setup(trace, runtime):
        del trace
        for name, payload in runtime_files(context, coordinate).items():
            await runtime.write(name, payload)
    task.setup = setup
    return task


def environment_config(arm):
    value = copy.deepcopy(sources()[1].qs.qnative().stack().interface.e.environment_config())
    value["agent"]["harness"]["max_depth"] = 0 if arm == "no_child_python" else 1
    value["agent"]["max_turns"] = 6
    value["agent"]["retries"] = {"max_retries": 0}
    value["agent"]["timeout"] = {"setup": 60, "rollout": 165, "finalize": 15, "scoring": 15}
    value["retries"] = {"max_retries": 0}
    return value


@functools.lru_cache(maxsize=2)
def binding(helper_arm):
    if helper_arm not in ("c32", "rl_step8"):
        raise ValueError("service requires one named helper")
    es, terminal, helper, _decoder, _causal = sources()
    value = copy.deepcopy(es.SOURCE_STUDY.binding())
    root = value["models"][value["role_map"]["root"]]
    if root["adapter_sha256"] != ROOT_SHA:
        raise ValueError("fixed QS6 root differs")
    terminal.fixed_start()
    if helper_arm == "rl_step8":
        eligibility = load("ag_live_original_rl_eligibility", HELPER / "eligibility.py", {"study": helper})
        endpoint = eligibility.qualify("rl_step8")
        updated = endpoint["binding"]["models"][helper.CHILD_ALIAS]
        if updated["adapter_sha256"] != RL_SHA:
            raise ValueError("not fixed original seed1 RL8")
        value["models"][value["fixed_child"]] = copy.deepcopy(updated)
    if value["models"][value["fixed_child"]]["adapter_sha256"] != (CHILD_SHA if helper_arm == "c32" else RL_SHA):
        raise ValueError("helper identity differs")
    value["whole_rlm_ag_transfer"] = {"study": ROOT.name, "helper_arm": helper_arm,
        "root_unchanged": True, "helper_calls": "live canonical B4 only", "training": False}
    return value


def verify():
    ready = read(ROOT / "READY.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity differs")
    for path, pin in ready["closure_sha256"].items():
        if sha(path) != pin:
            raise ValueError("source or input changed: " + path)
    return ready
