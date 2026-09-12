"""Frozen train-readout and heldout schedules for procedural-root SFT."""

from __future__ import annotations

import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE = SIDE / "openai-mrcr-short32-base-calibration-v1"
DATA = SIDE / "openai-mrcr-short-root-data-v1"
TRAINING = SIDE / "openai-mrcr-procedural-sft-warmstart-v1"
TRAIN_OUTPUT = TRAINING / "outputs/attempt-001"
BASE = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
TRAIN_PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/"
    "a100-lora-roundtrip/gpu/training/.venv/bin/python"
)
RUNTIME = SIDE / "runtime-an22-5801-v1"
ROLE_SOURCE = SIDE / "root-only-credit-v1/native_routing.py"
DUAL_SERVICE = RUNTIME / "service_wrapper_v2.py"
INPUTS = ROOT / "inputs"
READY_V1 = ROOT / "CPU_READY.json"
READY = ROOT / "CPU_READY_V2.json"
BASE_ALIAS = "Qwen3-4B-Instruct-2507-procedural-eval-zero"
ADAPTED_ALIAS = "Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step4"
OWNER_SECONDS = 900
SCIENCE_SECONDS = 600


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
def source():
    return load("procedural_sft_eval_short_source", SOURCE / "study.py")


@functools.lru_cache(maxsize=1)
def model_inputs():
    return read(DATA / "MODEL_INPUTS_V2.json")


def records(phase: str):
    split = "train" if phase == "train" else "heldout" if phase == "held" else None
    if split is None:
        raise ValueError("phase must be train or held")
    return model_inputs()[split]


@functools.lru_cache(maxsize=2)
def schedule(phase: str):
    values = []
    repeats = 1 if phase == "train" else 2
    base = 2026091600 if phase == "train" else 2026091700
    for index, row in enumerate(records(phase)):
        for repeat in range(repeats):
            coordinate = {
                "study": ROOT.name,
                "phase": phase,
                "record_id": row["id"],
                "source_row_sha256": row["source_row_sha256"],
                "ordered_core_sha256": row["ordered_core_sha256"],
                "context_sha256": row["prompt_json_sha256"],
                "row_index": index,
                "repeat": repeat,
                "seed": base + repeats * index + repeat,
                "temperature": 0.5,
            }
            values.append({**coordinate, "id": digest(coordinate)})
    return values


def input_dir(phase: str) -> Path:
    return INPUTS / phase


def prepare_inputs() -> dict:
    old = source().v7_study().old_module()
    teacher = load("procedural_sft_eval_teacher_renderer", TRAINING / "teacher.py")
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer

    system, tools = teacher._system_and_ordered_tools()
    renderer = create_renderer(
        load_tokenizer(str(BASE)), Qwen3RendererConfig(enable_thinking=True)
    )
    source_gold = read(DATA / "host/HOST_GOLD.json")
    report = {}
    for phase in ("train", "held"):
        directory = input_dir(phase)
        selected = {row["id"]: row for row in records(phase)}
        tasks, contexts = [], {}
        for row in selected.values():
            payload = Path(row["prompt_json_path"]).read_bytes()
            if hashlib.sha256(payload).hexdigest() != row["prompt_json_sha256"]:
                raise ValueError("frozen public context changed")
            context = directory / "contexts" / (row["prompt_json_sha256"] + ".json")
            context.parent.mkdir(parents=True, exist_ok=True)
            if context.exists():
                if context.read_bytes() != payload:
                    raise ValueError("prepared context differs")
            else:
                context.write_bytes(payload)
                context.chmod(0o444)
            contexts[row["id"]] = row["prompt_json_sha256"]
        for index, coordinate in enumerate(schedule(phase)):
            row = selected[coordinate["record_id"]]
            question = Path(row["final_question_path"]).read_text()
            tasks.append(
                old.MRCRData(
                    idx=index,
                    name=coordinate["id"],
                    prompt=source().root_prompt(question, row["prompt_json_bytes"]),
                    row_id=row["id"],
                    document_sha256=row["prompt_json_sha256"],
                    arm="procedural_sft_" + phase,
                ).model_dump(mode="json", exclude_none=True)
            )
        gold_split = "train" if phase == "train" else "heldout"
        gold = {row_id: source_gold[gold_split][row_id] for row_id in selected}
        prefixes = {}
        for task, coordinate in zip(tasks, schedule(phase), strict=True):
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
        values = [
            (directory / "tasks.json", tasks),
            (directory / "PREFIXES.json", prefixes),
            (
                directory / "PUBLIC.json",
                {
                    "phase": phase,
                    "plan": schedule(phase),
                    "record_ids": list(selected),
                    "context_sha256_by_record": contexts,
                    "gold_in_model_input": False,
                },
            ),
            (directory / "HOST_GOLD.json", gold),
        ]
        for path, value in values:
            if path.exists():
                if read(path) != value:
                    raise ValueError("immutable prepared input differs: " + str(path))
            else:
                write_x(path, value)
        (directory / "HOST_GOLD.json").chmod(0o600)
        report[phase] = {
            "records": len(selected),
            "episodes": len(tasks),
            "contexts": len(contexts),
            "prefixes": len(prefixes),
            "schedule_sha256": digest(schedule(phase)),
        }
    return report


def environment_config(phase: str):
    old = source().v7_study().old_module()
    return {
        "taskset": {"id": source().v7_study().OLD.name, "tasks_file": str(input_dir(phase) / "tasks.json")},
        "timeout": {"episode": 180, "finalize": 15},
        "interception": {"type": "server"},
        "agent": {
            "harness": {
                "id": source().v7_study().OLD.name,
                "version": old.NANO_COMMIT,
                "max_depth": 1,
            },
            "runtime": {"type": "docker", "image": source().IMAGE, "workdir": "/app"},
            "max_turns": 6,
            "timeout": {"setup": 60, "rollout": 165, "finalize": 15, "scoring": 15},
            "retries": {"max_retries": 0},
        },
        "retries": {"max_retries": 0},
    }


def environment(phase: str):
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(environment_config(phase)))
    mapping = {row["prompt_json_sha256"]: Path(row["prompt_json_path"]) for row in records(phase)}

    async def setup(self, trace, runtime):
        del trace
        path = mapping.get(self.data.document_sha256)
        if path is None:
            raise ValueError("task references context outside frozen phase")
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != self.data.document_sha256:
            raise ValueError("frozen original JSON changed")
        await runtime.write("/context.json", payload)
        actual = await runtime.read("/context.json")
        if hashlib.sha256(actual).hexdigest() != self.data.document_sha256:
            raise ValueError("runtime context write/read changed")

    classes = {type(task) for task in env.taskset}
    if len(classes) != 1:
        raise ValueError("expected one canonical MRCR task class")
    task_class = classes.pop()
    if task_class.__module__ != "mrcr_rootless_document_baseline_v2":
        raise ValueError("unexpected MRCR task implementation")
    task_class.setup = setup
    module = sys.modules.get("mrcr_rootless_document_baseline_v2")
    if module is None:
        raise ValueError("canonical MRCR harness module missing")
    version = env.config.agent.harness.version
    module.NANO_CACHE = "/tmp/vf-rlm-" + hashlib.sha256(version.encode()).hexdigest()
    return env


def official_grade():
    return source().official_grade()


def dependencies():
    suite = source().dependencies()
    suite.SERVE = DUAL_SERVICE
    suite.life.__dict__["ALLOCATION_SERVICE"] = DUAL_SERVICE
    return suite
