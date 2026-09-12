"""Frozen first-eight grouped rollout screen from procedural-SFT checkpoint 32.

The model's terminal output is evaluated under the narrow, process-local, qualified
``terminal-strip-disabled`` intervention. It is not a generally lossless parser.
"""

from __future__ import annotations

import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE_EVAL = SIDE / "openai-mrcr-procedural-sft-eval-v1"
CHECKPOINT_EVAL = SIDE / "openai-mrcr-procedural-sft-continue32-eval-v1"
TERMINAL_HOOK = SIDE / "openai-mrcr-procedural-sft-terminal-strip-disabled-v1"
SOURCE = SIDE / "openai-mrcr-short32-base-calibration-v1"
TRAINING = SIDE / "openai-mrcr-procedural-sft-continue32-v1"
TEACHER_SOURCE = SIDE / "openai-mrcr-procedural-sft-warmstart-v1/teacher.py"
TRAIN_OUTPUT = TRAINING / "outputs/attempt-001"
DATA = SIDE / "openai-mrcr-short-root-data-v1"
INPUTS = ROOT / "inputs"
READY = ROOT / "CPU_READY.json"
PREP_HOLD = ROOT / "PREP_HOLD.json"
OWNER_SECONDS = 1100
SCIENCE_SECONDS = 900
BASE = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
ADAPTED_ALIAS = "Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step32"
BASE_ALIAS = "Qwen3-4B-Instruct-2507-procedural-eval-zero"
ROLE_SOURCE = SIDE / "root-only-credit-v1/native_routing.py"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def read(path: Path):
    return json.loads(Path(path).read_text())


def write_x(path: Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def base_study():
    return load("sft32_onpolicy_base_study", SOURCE_EVAL / "study.py")


@functools.lru_cache(maxsize=1)
def terminal_hooks():
    ready = read(TERMINAL_HOOK / "CPU_READY.json")
    if (
        sha(TERMINAL_HOOK / "CPU_READY.json")
        != "686e484b6ffa0338b6b699537b10e4ea84f436a29d76baa0ec704f895a629d91"
        or ready.get("identity")
        != "f09078f6e68626be5d861752b7dabc6174572ec5c19e51d87222402f1d2efd31"
        or sha(TERMINAL_HOOK / "hooks.py")
        != "3361c4aa6e3063e7742f5166be45b4bea8b83eb370d8b774da2e08e8924849bf"
        or sha(TERMINAL_HOOK / "CPU_TESTS.json")
        != "60574f1c58598097d70d441f9b5afcce2632d1189f21ce0ece4a4b0f44d4684f"
    ):
        raise ValueError("terminal-strip-disabled qualification receipt changed")
    hooks = load("sft32_onpolicy_terminal_strip_hooks", TERMINAL_HOOK / "hooks.py")
    contract = hooks.qualify()
    if contract.get("condition") != "terminal-strip-disabled":
        raise ValueError("wrong terminal parser intervention")
    return hooks


@functools.lru_cache(maxsize=1)
def model_inputs():
    return read(DATA / "MODEL_INPUTS_V2.json")


def records(phase: str):
    if phase != "train":
        raise ValueError("the screen has exactly one training-only phase")
    return model_inputs()["train"][:8]


@functools.lru_cache(maxsize=1)
def schedule(phase: str):
    rows = []
    for index, record in enumerate(records(phase)):
        for repeat in range(4):
            coordinate = {
                "study": ROOT.name,
                "phase": "train",
                "record_id": record["id"],
                "source_row_sha256": record["source_row_sha256"],
                "ordered_core_sha256": record["ordered_core_sha256"],
                "context_sha256": record["prompt_json_sha256"],
                "row_index": index,
                "repeat": repeat,
                "seed": 202609200000 + 4 * index + repeat,
                "temperature": 0.5,
            }
            rows.append({**coordinate, "id": digest(coordinate)})
    return rows


def input_dir(phase: str) -> Path:
    if phase != "train":
        raise ValueError("the screen has exactly one training-only phase")
    return INPUTS / phase


def _bound_eval():
    """Return the proven evaluation study with this screen's exact scientific bindings."""
    module = base_study()
    module.ROOT = ROOT
    module.INPUTS = INPUTS
    module.READY = READY
    module.TRAINING = TRAINING
    module.TRAIN_OUTPUT = TRAIN_OUTPUT
    module.ADAPTED_ALIAS = ADAPTED_ALIAS
    module.records = records
    module.schedule = schedule
    module.input_dir = input_dir
    return module


def source():
    """Return the original calibration module expected by the inherited collector."""
    return _bound_eval().source()


def prepare_inputs() -> dict:
    old = source().v7_study().old_module()
    teacher = load("sft32_onpolicy_teacher", TEACHER_SOURCE)
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer

    system, tools = teacher._system_and_ordered_tools()
    renderer = create_renderer(
        load_tokenizer(str(BASE)), Qwen3RendererConfig(enable_thinking=True)
    )
    source_gold = read(DATA / "host/HOST_GOLD.json")["train"]
    selected = {row["id"]: row for row in records("train")}
    directory = input_dir("train")
    contexts = {}
    for row in selected.values():
        payload = Path(row["prompt_json_path"]).read_bytes()
        if hashlib.sha256(payload).hexdigest() != row["prompt_json_sha256"]:
            raise ValueError("frozen public context changed")
        context = directory / "contexts" / (row["prompt_json_sha256"] + ".json")
        context.parent.mkdir(parents=True, exist_ok=True)
        if context.exists() and context.read_bytes() != payload:
            raise ValueError("prepared context differs")
        if not context.exists():
            context.write_bytes(payload)
            context.chmod(0o444)
        contexts[row["id"]] = row["prompt_json_sha256"]

    tasks = []
    for index, coordinate in enumerate(schedule("train")):
        row = selected[coordinate["record_id"]]
        question = Path(row["final_question_path"]).read_text()
        tasks.append(
            old.MRCRData(
                idx=index,
                name=coordinate["id"],
                prompt=source().root_prompt(question, row["prompt_json_bytes"]),
                row_id=row["id"],
                document_sha256=row["prompt_json_sha256"],
                arm="procedural_sft32_onpolicy_screen",
            ).model_dump(mode="json", exclude_none=True)
        )
    gold = {row_id: source_gold[row_id] for row_id in selected}
    prefixes = {}
    for task, coordinate in zip(tasks, schedule("train"), strict=True):
        token_ids = renderer.render(
            [system, {"role": "user", "content": task["prompt"]}],
            tools=tools,
            add_generation_prompt=True,
        ).token_ids
        prefixes[coordinate["id"]] = {
            "token_ids": token_ids,
            "token_ids_sha256": digest(token_ids),
            "task_prompt_sha256": hashlib.sha256(task["prompt"].encode()).hexdigest(),
        }
    public = {
        "phase": "train",
        "plan": schedule("train"),
        "record_ids": list(selected),
        "context_sha256_by_record": contexts,
        "selection": "first eight records in frozen MODEL_INPUTS_V2 train order",
        "gold_in_model_input": False,
    }
    for path, value in (
        (directory / "tasks.json", tasks),
        (directory / "PREFIXES.json", prefixes),
        (directory / "PUBLIC.json", public),
        (directory / "HOST_GOLD.json", gold),
    ):
        if path.exists() and read(path) != value:
            raise ValueError("immutable prepared input differs: " + str(path))
        if not path.exists():
            write_x(path, value)
    (directory / "HOST_GOLD.json").chmod(0o600)
    return {
        "records": 8,
        "episodes": 32,
        "contexts": 8,
        "prefixes": 32,
        "schedule_sha256": digest(schedule("train")),
    }


def environment_config(phase: str):
    return _bound_eval().environment_config(phase)


def environment(phase: str):
    return _bound_eval().environment(phase)


def dependencies():
    return _bound_eval().dependencies()


def official_grade():
    return _bound_eval().official_grade()
