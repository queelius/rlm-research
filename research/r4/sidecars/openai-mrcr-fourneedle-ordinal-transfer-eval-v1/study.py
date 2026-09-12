"""Frozen four-needle ordinal-transfer schedule and procedural-root runtime."""

from __future__ import annotations

import functools
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PARENT = SIDE / "openai-mrcr-long-transfer-eval-v1"
DATA = SIDE / "openai-mrcr-fourneedle-ordinal-transfer-data-v1"
INPUTS = ROOT / "inputs"
READY = ROOT / "READY.json"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


parent = load("mrcr_fourneedle_parent_study", PARENT / "study.py")
for _name in dir(parent):
    if not _name.startswith("_"):
        globals()[_name] = getattr(parent, _name)

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PARENT = SIDE / "openai-mrcr-long-transfer-eval-v1"
DATA = SIDE / "openai-mrcr-fourneedle-ordinal-transfer-data-v1"
INPUTS = ROOT / "inputs"
READY = ROOT / "READY.json"
OWNER_SECONDS = 700
SCIENCE_SECONDS = 600


@functools.lru_cache(maxsize=1)
def model_inputs():
    payload = read(DATA / "MODEL_INPUTS.json")
    if set(payload) != {"records"} or len(payload["records"]) != 16:
        raise ValueError("four-needle public inventory changed")
    return {"records": [
        {**row, "source_row_sha256": row["row_sha256"]} for row in payload["records"]
    ]}


def records(phase="long"):
    if phase != "long":
        raise ValueError("only fixed ordinal-transfer phase is permitted")
    return model_inputs()["records"]


@functools.lru_cache(maxsize=1)
def schedule(phase="long"):
    if phase != "long":
        raise ValueError("only fixed ordinal-transfer phase is permitted")
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
            "seed": 202609260000 + index,
            "temperature": 0.5,
        }
        values.append({**coordinate, "id": digest(coordinate)})
    return values


def input_dir(phase="long"):
    if phase != "long":
        raise ValueError("only fixed ordinal-transfer phase is permitted")
    return INPUTS


# Bind the defining V1 module used by environment/config functions, not only this facade.
_globals = parent.environment.__globals__
_globals.update(ROOT=ROOT, SIDE=SIDE, DATA=DATA, INPUTS=INPUTS, READY=READY,
                OWNER_SECONDS=OWNER_SECONDS, SCIENCE_SECONDS=SCIENCE_SECONDS,
                model_inputs=model_inputs, records=records, schedule=schedule, input_dir=input_dir)


def prepare_inputs():
    old = source().v7_study().old_module()
    teacher = load("mrcr_fourneedle_teacher_renderer", eval_study().TRAINING / "teacher.py")
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer

    data_ready = read(DATA / "DATA_READY.json")
    if sha(DATA / "DATA_READY.json") != "3ff63cf269efaa8e3f9407722cf7c88714f95abf17eca5d2d701e399ab8c1861" or data_ready.get("identity") != "ec3c47913389d0e52bc7245812cc96ffdac90998d90e9def4c4fbcd58c063480":
        raise ValueError("frozen four-needle DATA_READY changed")
    system, tools = teacher._system_and_ordered_tools()
    renderer = create_renderer(load_tokenizer(str(BASE)), Qwen3RendererConfig(enable_thinking=True))
    source_gold = read(DATA / "host/HOST_GOLD.json")
    selected = {row["id"]: row for row in records()}
    tasks, contexts = [], {}
    for row in selected.values():
        payload = Path(row["prompt_json_path"]).read_bytes()
        if hashlib.sha256(payload).hexdigest() != row["prompt_json_sha256"]:
            raise ValueError("frozen four-needle context changed")
        context = INPUTS / "contexts" / f"{row['prompt_json_sha256']}.json"
        context.parent.mkdir(parents=True, exist_ok=True)
        if context.exists() and context.read_bytes() != payload:
            raise ValueError("prepared context differs")
        if not context.exists():
            context.write_bytes(payload)
            context.chmod(0o444)
        contexts[row["id"]] = row["prompt_json_sha256"]
    for index, coordinate in enumerate(schedule()):
        row = selected[coordinate["record_id"]]
        question = Path(row["final_question_path"]).read_text()
        if hashlib.sha256(question.encode()).hexdigest() != row["final_question_sha256"]:
            raise ValueError("frozen final question changed")
        tasks.append(old.MRCRData(idx=index, name=coordinate["id"],
            prompt=source().root_prompt(question, row["prompt_json_bytes"]), row_id=row["id"],
            document_sha256=row["prompt_json_sha256"], arm="fourneedle_ordinal_transfer").model_dump(mode="json", exclude_none=True))
    prefixes = {}
    for task, coordinate in zip(tasks, schedule(), strict=True):
        token_ids = renderer.render([system, {"role": "user", "content": task["prompt"]}], tools=tools, add_generation_prompt=True).token_ids
        if len(token_ids) > 8192:
            raise ValueError("neural root prefix exceeds fixed service limit")
        prefixes[coordinate["id"]] = {"token_ids": token_ids, "token_ids_sha256": digest(token_ids), "task_prompt_sha256": hashlib.sha256(task["prompt"].encode()).hexdigest()}
    values = ((INPUTS / "tasks.json", tasks), (INPUTS / "PREFIXES.json", prefixes),
        (INPUTS / "PUBLIC.json", {"phase": "long", "plan": schedule(), "record_ids": list(selected), "context_sha256_by_record": contexts, "seed_namespace": "202609260000+fixed-row-index", "third_occurrence": 8, "fourth_occurrence": 8, "gold_in_model_input": False}),
        (INPUTS / "HOST_GOLD.json", {key: source_gold[key] for key in selected}))
    for path, value in values:
        if path.exists() and read(path) != value:
            raise ValueError("immutable prepared input differs: " + str(path))
        if not path.exists():
            write_x(path, value)
    (INPUTS / "HOST_GOLD.json").chmod(0o600)
    return {"records": 16, "episodes": 16, "contexts": 16, "prefixes": 16, "schedule_sha256": digest(schedule())}


def environment_config(phase="long"):
    return parent.environment_config(phase)


def environment(phase="long"):
    return parent.environment(phase)


def official_grade():
    return parent.official_grade()


def dependencies():
    return parent.eval_study().dependencies()


def terminal_hooks():
    return parent.terminal_hooks()
