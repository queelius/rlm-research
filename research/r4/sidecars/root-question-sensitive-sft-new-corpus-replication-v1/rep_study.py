"""New-corpus QS replication facade over the qualified QS implementation."""
import functools
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
ORIGINAL = SIDE / "root-question-sensitive-sft-v1"
METADATA = SIDE / "root-question-sensitive-metadata-transfer-v1"
ATTEMPT = ROOT / "outputs/attempt-001"
sys.path.insert(0, str(ORIGINAL))
base = importlib.import_module("qs_study")
read, write, sha, digest, load, aliases = (
    base.read, base.write, base.sha, base.digest, base.load, base.aliases
)
OLD, JOINT, NATIVE, TRAIN, CT, CF, CHILD_SHA = (
    base.OLD, base.JOINT, base.NATIVE, base.TRAIN, base.CT, base.CF, base.CHILD_SHA
)
problem = base.problem
NAMESPACE = "question-sensitive-sft-new-corpus-replication-20260910-v1"
SEED = 992173003


def __getattr__(name):
    return getattr(base, name)


def starting_policy():
    return base.starting_policy()


def answer(records, labels, row):
    return base.answer(records, labels, row)


def make_task(context, row, gold):
    return qnative().make_task(context, row["question"], gold, row["id"])


runtime, interface, joint, qnative = base.runtime, base.interface, base.joint, base.qnative


@functools.lru_cache(maxsize=1)
def stack():
    native = qnative().stack().native

    def task(context, prompt, gold, name):
        query = read(ROOT / "inputs/PROMPTS_ACCURATE.json")[name]["plain_query"]
        value = qnative().make_task(context, query, gold, name)
        if value.data.prompt != prompt:
            raise ValueError("exact new-corpus native prefix")
        return value

    return SimpleNamespace(native=SimpleNamespace(**{**vars(native), "task": task}))


def corpus(limit=None):
    if limit not in (None, 72):
        raise ValueError("only the complete72 corpus is admissible")
    plan = read(ROOT / "inputs/TRAIN_PLAN.json")
    if len(plan) != 72:
        raise ValueError("exact72 source plan")
    if limit is None:
        ready_path = ATTEMPT / "capture/CORPUS_READY.json"
        ready = read(ready_path)
        if ready["identity"] != verify()["identity"] or ready["examples"] != 72:
            raise ValueError("complete72 captured corpus required")
        for path, pin in ready["files_sha256"].items():
            if sha(path) != pin:
                raise ValueError("captured corpus changed")
    values = []
    child_paths = []
    learning = importlib.import_module("qs_learning")
    for coordinate in plan:
        directory = ATTEMPT / "capture" / coordinate["id"]
        teacher = read(directory / "TEACHER.json")
        if teacher["episode_id"] != coordinate["id"] or teacher["coordinate"] != coordinate:
            raise ValueError("captured coordinate mismatch")
        if not teacher["prefix_ids_verified"] or teacher["masked_history_turns"]:
            raise ValueError("native prefix/history mismatch")
        if set(teacher["turns"]) != {"first_producer", "corrective", "terminal"}:
            raise ValueError("three authored root actions required")
        if len(teacher["actual_child_records"]) != 1:
            raise ValueError("one genuine child required")
        path = Path(teacher["actual_child_records"][0])
        if path.resolve().parent != (directory / "physical").resolve() or not path.exists():
            raise ValueError("episode-local actual child receipt required")
        physical = read(path)
        if physical.get("origin") != "actual c32" or not physical.get("physical_request_attempt"):
            raise ValueError("genuine c32 acquisition required")
        for turn in teacher["turns"].values():
            learning.validate_turn(turn)
        values.append(teacher); child_paths.append(str(path.resolve()))
    if len(set(child_paths)) != 72:
        raise ValueError("one distinct acquisition per teacher")
    return values


def verify():
    ready = read(ROOT / "READY.json")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError("frozen source/input changed " + path)
    starting_policy()
    return ready
