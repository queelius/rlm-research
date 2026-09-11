"""Immutable QS72 recovery boundary and combined-corpus verifier."""
import hashlib
import importlib
import json
from pathlib import Path
import sys

SOURCE_ROOT = Path(__file__).resolve().parent
SIDE = SOURCE_ROOT.parent
ORIGINAL = SIDE / "root-question-sensitive-sft-v1"
ROOT = ORIGINAL
ORIGINAL_ATTEMPT = ORIGINAL / "outputs/attempt-001"
ATTEMPT = SOURCE_ROOT / "outputs/attempt-001"
if str(ORIGINAL) not in sys.path:
    sys.path.insert(0, str(ORIGINAL))
base = importlib.import_module("qs_study")

read, write, sha, digest, aliases, load = (
    base.read, base.write, base.sha, base.digest, base.aliases, base.load
)
NATIVE, TRAIN, OLD, CT, CF, JOINT, CHILD_SHA = (
    base.NATIVE, base.TRAIN, base.OLD, base.CT, base.CF, base.JOINT, base.CHILD_SHA
)
NAMESPACE = "question-sensitive-sft72-recovery-20260910-v1"
SEED = base.SEED


def __getattr__(name):
    return getattr(base, name)


def train_plan():
    return read(ORIGINAL / "inputs/TRAIN_PLAN.json")


def learning():
    return importlib.import_module("qs_learning")


def capture_boundary():
    rows = []
    for index, coordinate in enumerate(train_plan()):
        directory = ORIGINAL_ATTEMPT / "capture" / coordinate["id"]
        teacher = directory / "TEACHER.json"
        episode = directory / "EPISODE.json"
        physical = sorted((directory / "physical").glob("*.json"))
        role = sorted((directory / "role-audit").glob("*.json"))
        typed = sorted((directory / "typed-audit").glob("*.json"))
        if index < 65:
            if not teacher.exists() or not episode.exists() or len(physical) != 4:
                raise ValueError("frozen completed prefix changed")
            disposition = "reuse_authenticated_teacher"
        elif index == 65:
            failure = directory / "FAILURE.json"
            if not failure.exists() or physical or role or typed:
                raise ValueError("coordinate65 is not an evidenced pre-request failure")
            disposition = "retry_after_pre_request_deadline_failure"
        else:
            if directory.exists():
                raise ValueError("original unstarted tail acquired artifacts")
            disposition = "first_attempt_after_original_unstarted"
        rows.append({
            "index": index, "id": coordinate["id"], "disposition": disposition,
            "original_teacher_sha256": sha(teacher) if teacher.exists() else None,
            "original_episode_sha256": sha(episode) if episode.exists() else None,
            "original_physical_records": len(physical),
            "original_role_audit_records": len(role),
            "original_typed_audit_records": len(typed),
        })
    return rows


def missing_indices(rows=None):
    rows = rows or capture_boundary()
    return [r["index"] for r in rows if r["disposition"] != "reuse_authenticated_teacher"]


def _validate_teacher(coordinate, teacher, expected):
    if teacher["episode_id"] != coordinate["id"] or teacher["coordinate"] != coordinate:
        raise ValueError("captured coordinate mismatch")
    if not teacher["prefix_ids_verified"] or teacher["masked_history_turns"]:
        raise ValueError("native prefix/history mismatch")
    if set(teacher["turns"]) != {"first_producer", "corrective", "terminal"}:
        raise ValueError("three authored root actions required")
    paths = teacher["actual_child_records"]
    if len(paths) != 1:
        raise ValueError("one genuine child required")
    path = Path(paths[0])
    if path.resolve().parent != expected.resolve() or not path.exists():
        raise ValueError("episode-local child receipt required")
    physical = read(path)
    if physical.get("origin") != "actual c32" or not physical.get("physical_request_attempt"):
        raise ValueError("actual c32 receipt required")
    for turn in teacher["turns"].values():
        learning().validate_turn(turn)
    return path


def build_corpus_ready():
    boundary = capture_boundary()
    values, pins, child_paths = [], {}, []
    for index, coordinate in enumerate(train_plan()):
        source = ORIGINAL_ATTEMPT if index < 65 else ATTEMPT
        directory = source / "capture" / coordinate["id"]
        teacher_path = directory / "TEACHER.json"
        episode_path = directory / "EPISODE.json"
        if not teacher_path.exists() or not episode_path.exists():
            raise ValueError("complete fixed72 recovery corpus required")
        teacher = read(teacher_path)
        child = _validate_teacher(coordinate, teacher, directory / "physical")
        child_paths.append(str(child.resolve())); values.append(teacher)
        pins[str(teacher_path)] = sha(teacher_path); pins[str(episode_path)] = sha(episode_path)
        pins[str(child)] = sha(child)
    if len(set(child_paths)) != 72:
        raise ValueError("separate actual acquisition per trajectory")
    receipt = {
        "identity": verify()["identity"], "examples": 72, "reused_original": 65,
        "new_recovery": 7, "boundary": boundary, "files_sha256": pins,
        "retry_policy": "coordinate65 explicit retry after evidenced pre-request failure; 66-71 first attempt; no completed response resampled",
    }
    write(ATTEMPT / "capture/CORPUS_READY.json", receipt)
    return values


def corpus(limit=None):
    if limit == 72:
        return build_corpus_ready()
    if limit is not None: raise ValueError("recovery admits only complete72 corpus")
    receipt = read(ATTEMPT / "capture/CORPUS_READY.json")
    if receipt["identity"] != verify()["identity"] or receipt["examples"] != 72:
        raise ValueError("combined corpus identity")
    for path, pin in receipt["files_sha256"].items():
        if sha(path) != pin:
            raise ValueError("combined corpus changed")
    return [read(ORIGINAL_ATTEMPT / "capture" / r["id"] / "TEACHER.json") if i < 65
            else read(ATTEMPT / "capture" / r["id"] / "TEACHER.json")
            for i, r in enumerate(train_plan())]


def starting_policy():
    return base.starting_policy()


def runtime():
    return base.runtime()


def baseline_reference():
    terminal = ORIGINAL_ATTEMPT / "OWNER_TERMINAL.json"
    if not terminal.exists():
        raise ValueError("original owner must finish before recovery")
    value = read(terminal)
    if value.get("elapsed_seconds", 10801) + 5400 > 10800:
        raise ValueError("combined original actual plus recovery cap exceeds10800")
    rows = [r for r in value["readout_inventory"] if r["policy"] == "unchanged"]
    if len(rows) != 80:
        raise ValueError("exact original baseline80 inventory")
    pins = {}
    for row in rows:
        path = Path(row["path"])
        for candidate in [path, path.parent / "FAILURE.json", *sorted((path.parent / "physical").glob("*.json"))]:
            if candidate.exists(): pins[str(candidate)] = sha(candidate)
    return {"planned": 80, "source_owner_terminal": str(terminal),
            "source_owner_terminal_sha256": sha(terminal), "rows": rows, "artifact_sha256": pins}


def verify():
    ready_path = SOURCE_ROOT / "READY.json"
    ready = read(ready_path)
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin: raise ValueError("READY changed " + path)
    capture_boundary(); starting_policy()
    return ready
