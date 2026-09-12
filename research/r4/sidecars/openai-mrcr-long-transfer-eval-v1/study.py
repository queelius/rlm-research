"""Frozen long-input MRCR transfer schedule and exact procedural-root runtime."""

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
DATA = SIDE / "openai-mrcr-long-transfer-data-v1"
SOURCE_EVAL = SIDE / "openai-mrcr-procedural-sft-eval-v1"
SOURCE = SIDE / "openai-mrcr-short32-base-calibration-v1"
CHECKPOINT_EVAL = SIDE / "openai-mrcr-procedural-sft-continue32-eval-v1"
TERMINAL_HOOK = SIDE / "openai-mrcr-procedural-sft-terminal-strip-disabled-v1"
TRAINING = SIDE / "openai-mrcr-procedural-sft-continue32-v1"
TRAIN_OUTPUT = TRAINING / "outputs/attempt-001"
BASE = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
ROLE_SOURCE = SIDE / "root-only-credit-v1/native_routing.py"
INPUTS = ROOT / "inputs"
READY = ROOT / "READY.json"
BASE_ALIAS = "Qwen3-4B-Instruct-2507-procedural-eval-zero"
ADAPTED_ALIAS = "Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step32"
OWNER_SECONDS = 1100
SCIENCE_SECONDS = 900


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
def eval_study():
    return load("mrcr_long_transfer_source_study", SOURCE_EVAL / "study.py")


@functools.lru_cache(maxsize=1)
def source():
    """Expose the exact short-MRCR study expected by the inherited collector."""
    return eval_study().source()


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
    hooks = load("mrcr_long_transfer_terminal_strip_hooks", TERMINAL_HOOK / "hooks.py")
    contract = hooks.qualify()
    if contract.get("condition") != "terminal-strip-disabled":
        raise ValueError("wrong terminal parser intervention")
    return hooks


@functools.lru_cache(maxsize=1)
def model_inputs():
    payload = read(DATA / "MODEL_INPUTS.json")
    if payload.get("schema") != "openai-mrcr-long-transfer-public-inputs-v1":
        raise ValueError("long-transfer input schema changed")
    return payload


def records(phase: str = "long"):
    if phase != "long":
        raise ValueError("only the frozen long-transfer phase is permitted")
    return model_inputs()["records"]


@functools.lru_cache(maxsize=1)
def schedule(phase: str = "long"):
    if phase != "long":
        raise ValueError("only the frozen long-transfer phase is permitted")
    values = []
    for index, row in enumerate(records()):
        coordinate = {
            "study": ROOT.name,
            "phase": "long",
            "record_id": row["id"],
            "source_row_sha256": row["source_row_sha256"],
            "ordered_core_sha256": row["ordered_core_sha256"],
            "context_sha256": row["prompt_json_sha256"],
            "row_index": index,
            "repeat": 0,
            "seed": 202609210000 + index,
            "temperature": 0.5,
        }
        values.append({**coordinate, "id": digest(coordinate)})
    return values


def input_dir(phase: str = "long") -> Path:
    if phase != "long":
        raise ValueError("only the frozen long-transfer phase is permitted")
    return INPUTS


def prepare_inputs() -> dict:
    old = source().v7_study().old_module()
    teacher = load("mrcr_long_transfer_teacher_renderer", eval_study().TRAINING / "teacher.py")
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer

    data_ready = read(DATA / "DATA_READY.json")
    if (
        sha(DATA / "DATA_READY.json")
        != "d4d82f86a5d1c8b88d6e3bcc5a15fabfaadc1f1f44fa628f2c9e5207d7ed48c2"
        or data_ready.get("identity")
        != "609dc317e86aa09e18e03a1b6d131c374db4b266ee0a7a18cce974e30029598a"
    ):
        raise ValueError("frozen long-transfer DATA_READY changed")
    system, tools = teacher._system_and_ordered_tools()
    renderer = create_renderer(
        load_tokenizer(str(BASE)), Qwen3RendererConfig(enable_thinking=True)
    )
    source_gold = read(DATA / "host/HOST_GOLD.json")
    selected = {row["id"]: row for row in records()}
    tasks, contexts = [], {}
    for row in selected.values():
        payload = Path(row["prompt_json_path"]).read_bytes()
        if hashlib.sha256(payload).hexdigest() != row["prompt_json_sha256"]:
            raise ValueError("frozen public long context changed")
        context = INPUTS / "contexts" / f"{row['prompt_json_sha256']}.json"
        context.parent.mkdir(parents=True, exist_ok=True)
        if context.exists():
            if context.read_bytes() != payload:
                raise ValueError("prepared long context differs")
        else:
            context.write_bytes(payload)
            context.chmod(0o444)
        contexts[row["id"]] = row["prompt_json_sha256"]
    for index, coordinate in enumerate(schedule()):
        row = selected[coordinate["record_id"]]
        question = Path(row["final_question_path"]).read_text()
        if hashlib.sha256(question.encode()).hexdigest() != row["final_question_sha256"]:
            raise ValueError("frozen final question changed")
        tasks.append(
            old.MRCRData(
                idx=index,
                name=coordinate["id"],
                prompt=source().root_prompt(question, row["prompt_json_bytes"]),
                row_id=row["id"],
                document_sha256=row["prompt_json_sha256"],
                arm="long_transfer",
            ).model_dump(mode="json", exclude_none=True)
        )
    gold = {row_id: source_gold[row_id] for row_id in selected}
    prefixes = {}
    for task, coordinate in zip(tasks, schedule(), strict=True):
        token_ids = renderer.render(
            [system, {"role": "user", "content": task["prompt"]}],
            tools=tools,
            add_generation_prompt=True,
        ).token_ids
        if len(token_ids) > 8192:
            raise ValueError("neural root initial prefix exceeds fixed 8192-token service limit")
        prefixes[coordinate["id"]] = {
            "token_ids": token_ids,
            "token_ids_sha256": digest(token_ids),
            "task_prompt_sha256": hashlib.sha256(task["prompt"].encode()).hexdigest(),
        }
    values = [
        (INPUTS / "tasks.json", tasks),
        (INPUTS / "PREFIXES.json", prefixes),
        (
            INPUTS / "PUBLIC.json",
            {
                "phase": "long",
                "plan": schedule(),
                "record_ids": list(selected),
                "context_sha256_by_record": contexts,
                "seed_namespace": "202609210000+fixed-row-index",
                "gold_in_model_input": False,
                "external_file_length_is_not_neural_root_prompt_length": True,
            },
        ),
        (INPUTS / "HOST_GOLD.json", gold),
    ]
    for path, value in values:
        if path.exists():
            if read(path) != value:
                raise ValueError("immutable prepared input differs: " + str(path))
        else:
            write_x(path, value)
    (INPUTS / "HOST_GOLD.json").chmod(0o600)
    return {
        "records": len(selected),
        "episodes": len(tasks),
        "contexts": len(contexts),
        "prefixes": len(prefixes),
        "schedule_sha256": digest(schedule()),
    }


def environment_config(phase: str = "long"):
    if phase != "long":
        raise ValueError("only the frozen long-transfer phase is permitted")
    old = source().v7_study().old_module()
    return {
        "taskset": {"id": source().v7_study().OLD.name, "tasks_file": str(INPUTS / "tasks.json")},
        "timeout": {"episode": 240, "finalize": 15},
        "interception": {"type": "server"},
        "agent": {
            "harness": {"id": source().v7_study().OLD.name, "version": old.NANO_COMMIT, "max_depth": 1},
            "runtime": {"type": "docker", "image": source().IMAGE, "workdir": "/app"},
            "max_turns": 6,
            "timeout": {"setup": 60, "rollout": 225, "finalize": 15, "scoring": 15},
            "retries": {"max_retries": 0},
        },
        "retries": {"max_retries": 0},
    }


def environment(phase: str = "long"):
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(environment_config(phase)))
    mapping = {row["prompt_json_sha256"]: Path(row["prompt_json_path"]) for row in records()}

    async def setup(self, trace, runtime):
        del trace
        path = mapping.get(self.data.document_sha256)
        if path is None:
            raise ValueError("task references context outside frozen long cohort")
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != self.data.document_sha256:
            raise ValueError("frozen original long JSON changed")
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
    return source().dependencies()
