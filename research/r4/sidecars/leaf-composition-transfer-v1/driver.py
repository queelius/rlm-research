"""Bind frozen new contexts to the independently qualified child-role treatment."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROLE = ROOT.parent / "leaf-role-routing-v1"
sys.path.insert(0, str(ROLE / "source"))
loader = importlib.util.spec_from_file_location(
    "composition_role_driver", ROLE / "source/driver.py"
)
role = importlib.util.module_from_spec(loader)
loader.loader.exec_module(role)


def load_inputs():
    manifest = json.loads((ROOT / "prepared-v1/MANIFEST.json").read_text())
    if role.digest({k: v for k, v in manifest.items() if k != "identity"}) != manifest["identity"]:
        raise ValueError("composition manifest identity changed")
    paths = dict(manifest["source_sha256"])
    paths[str(ROOT / "prepared-v1/DATA.json")] = manifest["data_sha256"]
    for path, expected in paths.items():
        if role.file_hash(path) != expected:
            raise ValueError(f"composition source changed: {path}")
    return manifest, json.loads((ROOT / "prepared-v1/DATA.json").read_text())


def make_tasks(data):
    from oolong_prime_rlm_strict_v1.taskset import StrictOolongConfig, StrictOolongTask
    from oolong_prime_v1.taskset import (
        _QUESTION_INSTRUCTION,
        _RLM_FILE_INSTRUCTION,
        OolongData,
    )
    from tokenizers import Tokenizer

    base = json.loads((role.SFT / "RECIPE.json").read_text())["base"]
    tokenizer = Tokenizer.from_file(str(Path(base) / "tokenizer.json"))
    contexts = {context["id"]: context for context in data["contexts"]}
    tasks = {}
    config = StrictOolongConfig()
    for index, row in enumerate(data["tasks"]):
        context = contexts[row["context_id"]]
        prompt = (
            _QUESTION_INSTRUCTION
            + "\n\n"
            + _RLM_FILE_INSTRUCTION
            + "\n\nQuestion: "
            + row["question"]
        )
        tasks[row["name"]] = StrictOolongTask(
            OolongData(
                idx=index,
                name=row["name"],
                prompt=prompt,
                source_id=row["source_id"],
                source_split="official-TREC-test-local-composition",
                source_revision=data["source_split_sha256"],
                dataset="local-trec-test-count-composition-v1",
                context_len=len(tokenizer.encode(context["text"], add_special_tokens=False).ids),
                context_window_id=row["context_window_id"],
                answer=row["answer"],
                answer_type=row["answer_type"],
                task_kind="local-count-by-coarse-category",
                context=context["text"],
            ),
            config.task,
        )
    return tasks


def make_spec():
    manifest, data = load_inputs()
    tasks = make_tasks(data)
    plan = [
        {**row, "task_hash": role.with_prompt(tasks[row["task_name"]], row["arm"]).hash}
        for row in data["plan"]
    ]
    endpoint = {
        "url": "http://127.0.0.1:18601/v1",
        "model": role.ORIGINAL,
        "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY",
        "renderer_model": json.loads((role.SFT / "RECIPE.json").read_text())["base"],
    }
    spec = role.make_spec(endpoint, None, tasks, plan, ROOT.name)
    spec.update(
        composition_identity=manifest["identity"],
        independent_contexts=6,
        unique_source_questions=384,
        source_question_overlap_with_component_test=True,
        source_question_overlap_with_sft_train_validation=False,
        interpretation=(
            "New count composition of component-test questions under the same supplied "
            "parsing/delegation example; not an untouched-source or learned-planning claim"
        ),
    )
    spec["source_file_sha256"].update(manifest["source_sha256"])
    paths = (
        Path(__file__),
        ROOT / "test_driver.py",
        ROOT / "prepared-v1/DATA.json",
        ROOT / "prepared-v1/MANIFEST.json",
    )
    spec["source_file_sha256"].update({str(path): role.file_hash(path) for path in paths})
    return spec, tasks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run"))
    parser.add_argument("--binding", type=Path, default=ROLE / "BOUND_WEIGHTS.json")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/attempt-001")
    args = parser.parse_args()
    spec, tasks = make_spec()
    path = ROOT / "SPEC.json"
    if args.command == "prepare":
        role.write_once(path, spec)
        print(json.dumps({"prepared": len(spec["plan"]), "spec_sha256": role.file_hash(path)}))
    else:
        if json.loads(path.read_text()) != spec:
            raise ValueError("frozen composition/run sources changed")
        binding = json.loads(args.binding.read_text())
        raise SystemExit(asyncio.run(role.run_study(spec, tasks, args.output, binding)))


if __name__ == "__main__":
    main()
