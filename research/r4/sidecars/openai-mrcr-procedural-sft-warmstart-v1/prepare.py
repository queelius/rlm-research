"""Seal the public-input-only teacher corpus; this performs no optimizer update."""

from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import time

import teacher


ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "openai-mrcr-short-root-data-v1"
SHORT = ROOT.parent / "openai-mrcr-short32-base-calibration-v1"


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode()
    ).hexdigest()


def write_x(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def load_official():
    spec = importlib.util.spec_from_file_location(
        "procedural_sft_official_score", DATA / "official_score.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def prepare() -> dict:
    started = time.monotonic()
    source = json.loads((DATA / "MODEL_INPUTS_V2.json").read_text())
    gold = json.loads((DATA / "host/HOST_GOLD.json").read_text())["train"]
    official = load_official()
    attempts = []
    failures = []
    for row in source["train"]:
        try:
            question = Path(row["final_question_path"]).read_text()
            payload = Path(row["prompt_json_path"]).read_bytes()
            result = teacher.construct(question, json.loads(payload))
            executed = teacher.execute_authored_code(result["authored_code"], payload)
            expected = gold[row["id"]]["answer"]
            score = official.grade(executed.removesuffix("\n"), expected, result["criteria"]["marker"])
            attempts.append(
                {
                    "record_id": row["id"],
                    "status": "exact" if executed == expected + "\n" and score == 1.0 else "wrong",
                    "criteria": result["criteria"],
                    "matching_user_indices": result["matching_user_indices"],
                    "selected_message_index": result["selected_message_index"],
                    "answer_sha256": hashlib.sha256(result["answer"].encode()).hexdigest(),
                    "host_gold_sha256": hashlib.sha256(expected.encode()).hexdigest(),
                    "official_score": score,
                    "program_stdout_exact_host_gold_plus_newline": executed == expected + "\n",
                }
            )
            if attempts[-1]["status"] != "exact":
                failures.append(attempts[-1])
        except BaseException as error:
            failure = {
                "record_id": row["id"],
                "status": "teacher_error",
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
            attempts.append(failure)
            failures.append(failure)
    audit = {
        "schema": "openai-mrcr-procedural-teacher-audit-v1",
        "attempted_train_records": len(attempts),
        "exact_train_records": sum(row["status"] == "exact" for row in attempts),
        "failures": failures,
        "attempts": attempts,
        "construction_inputs": ["public final question", "original public JSON conversation"],
        "host_gold_role": "post-construction exact audit and supervised target, never a selector",
        "host_gold_index_in_model_input": False,
        "heldout_query_files_read": 0,
        "heldout_context_files_read": 0,
        "heldout_gold_records_used": 0,
        "silent_filtering": False,
    }
    write_x(ROOT / "TEACHER_AUDIT_V2.json", audit)
    if failures or len(attempts) != 32:
        write_x(
            ROOT / "TEACHER_NOT_READY.json",
            {
                "status": "NOT_READY",
                "reason": "generic teacher did not exactly solve every frozen train record",
                "teacher_audit_sha256": teacher.sha(ROOT / "TEACHER_AUDIT_V2.json"),
            },
        )
        return audit
    corpus = teacher.render_training_rows()
    write_x(ROOT / "TEACHER_CORPUS_V2.json", corpus)
    smoke = json.loads((SHORT / "cpu-child-smoke-v2/PROVIDER_REQUESTS.json").read_text())
    first_action = corpus["episodes"][0]["turns"][0]
    action_tokens = [episode["turns"][0]["target_tokens"] for episode in corpus["episodes"]]
    terminal_tokens = [episode["turns"][1]["target_tokens"] for episode in corpus["episodes"]]
    lengths = [
        len(turn["input_ids"])
        for episode in corpus["episodes"]
        for turn in episode["turns"]
    ]
    fixture = {
        "schema": "openai-mrcr-procedural-renderer-fixture-v1",
        "actual_short32_first_prefix_equal": first_action["input_ids"][
            : first_action["prompt_length"]
        ]
        == smoke[0]["token_ids"],
        "actual_short32_first_prefix_sha256": digest(smoke[0]["token_ids"]),
        "rendered_first_prefix_sha256": digest(
            first_action["input_ids"][: first_action["prompt_length"]]
        ),
        "episodes": len(corpus["episodes"]),
        "root_action_target_tokens": {
            "total_per_pass": sum(action_tokens),
            "min": min(action_tokens),
            "max": max(action_tokens),
        },
        "terminal_target_tokens": {
            "total_per_pass": sum(terminal_tokens),
            "min": min(terminal_tokens),
            "max": max(terminal_tokens),
        },
        "maximum_training_sequence_tokens": max(lengths),
        "all_sequences_within_8192": max(lengths) <= 8192,
        "prompt_tool_child_tokens_masked": True,
        "root_action_and_terminal_tracked_separately": True,
    }
    write_x(ROOT / "RENDERER_FIXTURE_V2.json", fixture)
    inventory = {
        "schema": "openai-mrcr-procedural-sft-teacher-cpu-ready-v1",
        "status": "TEACHER_CORPUS_CPU_READY_NO_GPU_TRAINING_COMMAND_YET",
        "created_epoch": time.time(),
        "elapsed_cpu_seconds": time.monotonic() - started,
        "teacher": {
            "attempted": len(attempts),
            "exact": len(attempts) - len(failures),
            "failures": len(failures),
            "ordinals": dict(Counter(str(row["criteria"]["ordinal"]) for row in attempts)),
            "kinds": dict(Counter(row["criteria"]["kind"] for row in attempts)),
        },
        "heldout": {
            "records": len(source["heldout"]),
            "query_files_read": 0,
            "context_files_read": 0,
            "gold_records_used": 0,
            "model_queries": 0,
        },
        "optimizer_steps": 0,
        "gpu_calls": 0,
        "files_sha256": {
            str(path): teacher.sha(path)
            for path in [
                ROOT / "DESIGN.md",
                ROOT / "teacher.py",
                ROOT / "prepare.py",
                ROOT / "test_teacher.py",
                ROOT / "TEACHER_AUDIT_V2.json",
                ROOT / "TEACHER_CORPUS_V2.json",
                ROOT / "RENDERER_FIXTURE_V2.json",
                DATA / "MODEL_INPUTS_V2.json",
                DATA / "official_score.py",
                SHORT / "READY_V2.json",
                SHORT / "cpu-child-smoke-v2/PROVIDER_REQUESTS.json",
            ]
        },
        "next_gate": "MAIN review before implementing/sealing the fixed four-update trainer",
    }
    inventory["identity"] = digest(inventory)
    write_x(ROOT / "CPU_READY_TEACHER_V2.json", inventory)
    return inventory


if __name__ == "__main__":
    result = prepare()
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result.get("status", "").startswith("TEACHER_CORPUS_CPU_READY") else 1)
