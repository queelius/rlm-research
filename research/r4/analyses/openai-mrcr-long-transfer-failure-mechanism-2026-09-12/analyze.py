"""Read-only mechanism audit of the six checkpoint32 long-context failures.

Generated model programs are inspected as inert strings and are never executed.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from transformers import AutoTokenizer


ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
EVAL = STORE / "sidecars/openai-mrcr-long-transfer-eval-v1"
DATA = STORE / "sidecars/openai-mrcr-long-transfer-data-v1"
SCIENCE = EVAL / "outputs/checkpoint32-002/science"
SOURCE_ANALYSIS = STORE / "analyses/openai-mrcr-long-transfer-independent-2026-09-12/outcome"
TOKENIZER = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
SOURCE_SHA256: dict[str, str] = {}


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path: Path):
    path = Path(path)
    SOURCE_SHA256[str(path)] = sha(path)
    return json.loads(path.read_text())


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def native_rows(trace_id: str):
    rows = []
    for path in sorted((SCIENCE / "native-calls").glob("*-result.json")):
        item = json.loads(path.read_text())
        if item.get("session_id") == trace_id:
            SOURCE_SHA256[str(path)] = sha(path)
            rows.append(item)
    return rows


def tool_observations(trace):
    return [
        (node.get("message") or {}).get("content")
        for node in trace.get("nodes") or []
        if (node.get("message") or {}).get("role") == "tool"
        and isinstance((node.get("message") or {}).get("content"), str)
    ]


def generated_programs(trace):
    return [
        call.get("arguments", "")
        for node in trace.get("nodes") or []
        for call in ((node.get("message") or {}).get("tool_calls") or [])
        if call.get("name") == "ipython"
    ]


def build():
    SOURCE_SHA256.clear()
    prior = read(SOURCE_ANALYSIS / "RESULTS.json")
    gold = read(EVAL / "inputs/HOST_GOLD.json")
    model_inputs = read(DATA / "MODEL_INPUTS.json")["records"]
    by_record = {row["id"]: row for row in model_inputs}
    contract = read(SCIENCE / "TERMINAL_STRIP_CONTRACT.json")
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, local_files_only=True)
    for name in ("tokenizer.json", "tokenizer_config.json"):
        SOURCE_SHA256[str(TOKENIZER / name)] = sha(TOKENIZER / name)

    failed = [
        value
        for value in prior["stages"]["checkpoint32"]["records"].values()
        if value["available"] and not value["raw_exact"]
    ]
    rows = []
    integrity = []
    for prior_row in sorted(failed, key=lambda value: value["coordinate"]["row_index"]):
        path = Path(prior_row["episode_path"])
        episode = read(path)
        coordinate = episode["coordinate"]
        record_id = coordinate["record_id"]
        trace = episode["episode"]["traces"][0]
        reply = trace.get("root_reply")
        answer = gold[record_id]["answer"]
        marker = gold[record_id]["random_string_to_prepend"]
        observations = tool_observations(trace)
        programs = generated_programs(trace)
        native = native_rows(trace["id"])
        returned = [item for item in native if item.get("status") == "returned"]
        last = returned[-1]
        ids = last["response"]["tokens"]["completion_ids"]
        decoded = tokenizer.decode(ids, skip_special_tokens=False)
        suffix = "<|im_end|>"
        decoded_payload = decoded[: -len(suffix)] if decoded.endswith(suffix) else None
        score = (
            SequenceMatcher(None, reply.removeprefix(marker), answer.removeprefix(marker)).ratio()
            if isinstance(reply, str) and reply.startswith(marker)
            else 0.0
        )
        exact_observation = next(
            (value for value in observations if value in {answer, answer + "\n"}), None
        )
        program_text = ""
        if programs:
            try:
                program_text = json.loads(programs[0]).get("code", "")
            except json.JSONDecodeError:
                integrity.append(f"generated arguments not JSON:{coordinate['id']}")

        final_question = Path(by_record[record_id]["final_question_path"]).read_text()
        public_context = json.loads(Path(by_record[record_id]["prompt_json_path"]).read_text())
        request_match = re.search(r"request_text\s*=\s*(['\"])(.*?)\1", program_text)
        request_text = request_match.group(2) if request_match else None
        request_matches = sum(
            item.get("role") == "user"
            and isinstance(item.get("content"), str)
            and item["content"].strip().casefold() == (request_text or "").casefold()
            for item in public_context[:-1]
        )
        wrong_object_selector = bool(
            request_text
            and "program" in request_text.casefold()
            and "email" in final_question.casefold()
            and request_matches == 0
        )
        copy_only = bool(
            exact_observation is not None
            and isinstance(reply, str)
            and answer.endswith("  ")
            and reply == answer[:-2]
        )
        category = "terminal_dropped_two_spaces" if copy_only else "selector_retrieval_failure"
        if category == "selector_retrieval_failure" and not (
            wrong_object_selector
            and any("requested ordinal is unavailable" in value for value in observations)
            and reply == ""
            and last["response"].get("finish_reason") == "length"
        ):
            integrity.append(f"unexpected retrieval-failure mechanism:{coordinate['id']}")
        if copy_only and not (
            decoded_payload == reply
            and last["response"].get("finish_reason") == "stop"
            and exact_observation == answer + "\n"
        ):
            integrity.append(f"unexpected terminal transport evidence:{coordinate['id']}")
        rows.append(
            {
                "coordinate_id": coordinate["id"],
                "record_id": record_id,
                "source_row_sha256": coordinate["source_row_sha256"],
                "category": category,
                "available": episode["derived"]["scientifically_available"],
                "raw_exact": False,
                "official_marker_gated_sequence_matcher_similarity": score,
                "answer_sha256": hashlib.sha256(answer.encode()).hexdigest(),
                "reply_sha256": hashlib.sha256(reply.encode()).hexdigest(),
                "answer_utf8_bytes": len(answer.encode()),
                "reply_utf8_bytes": len(reply.encode()),
                "answer_terminal_codepoints": [ord(value) for value in answer[-4:]],
                "reply_terminal_codepoints": [ord(value) for value in reply[-4:]],
                "reply_equals_answer_without_final_two_ascii_spaces": copy_only,
                "clean_target_observation": exact_observation is not None,
                "clean_observation_sha256": (
                    hashlib.sha256(exact_observation.encode()).hexdigest()
                    if exact_observation is not None
                    else None
                ),
                "clean_observation_equals_answer_plus_linefeed": exact_observation == answer + "\n",
                "tool_observation_count": len(observations),
                "tool_observation_bytes": sum(len(value.encode()) for value in observations),
                "first_program_sha256": (
                    hashlib.sha256(program_text.encode()).hexdigest() if program_text else None
                ),
                "first_program_chars": len(program_text),
                "program_selects_wrong_object_type": wrong_object_selector,
                "program_selector_exact_context_matches": request_matches,
                "tool_error_requested_ordinal_unavailable": any(
                    "requested ordinal is unavailable" in value for value in observations
                ),
                "native_root_calls": len(returned),
                "native_last_finish_reason": last["response"].get("finish_reason"),
                "native_last_completion_tokens": len(ids),
                "native_last_decode_ends_im_end": decoded.endswith(suffix),
                "native_last_decoded_payload_equals_parsed_root_reply": decoded_payload == reply,
                "terminal_strip_condition": contract["condition"],
                "episode_path": str(path),
                "episode_sha256": SOURCE_SHA256[str(path)],
                "generated_program_executed_by_analyzer": False,
            }
        )
    counts = Counter(row["category"] for row in rows)
    if len(rows) != 6 or counts != Counter(
        {"terminal_dropped_two_spaces": 5, "selector_retrieval_failure": 1}
    ):
        integrity.append("failure inventory differs from frozen six/five/one expectation")
    return {
        "schema": "openai-mrcr-long-transfer-failure-mechanism-v1",
        "analyzed_source_created_epoch": prior["created_epoch"],
        "status": "COMPLETE_RAW_AUDIT" if not integrity else "HOLD_INTEGRITY_ERRORS",
        "failed_available_endpoints": len(rows),
        "categories": dict(counts),
        "rows": rows,
        "integrity_errors": integrity,
        "terminal_condition": contract["condition"],
        "generated_programs_executed": False,
        "source_sha256": dict(SOURCE_SHA256),
        "interpretation_limits": [
            "Five exact extraction observations followed by missing terminal spaces are observed transport failures, not proof of internal reasoning.",
            "The one selector mismatch is one fixed sample and does not estimate retrieval-error prevalence.",
            "All 16 long contexts are one-shot same-task transfer units; base pretraining exposure remains unknown.",
        ],
    }


def report(value):
    rows = value["rows"]
    copies = [row for row in rows if row["category"] == "terminal_dropped_two_spaces"]
    retrieval = next(row for row in rows if row["category"] == "selector_retrieval_failure")
    scores = [row["official_marker_gated_sequence_matcher_similarity"] for row in copies]
    return f"""---
schema: openai-mrcr-long-transfer-failure-mechanism-report-v1
status: {value['status']}
---

# Why checkpoint 32 missed six long-context endpoints

The five copy failures are exact and homogeneous: each Python observation equals the host answer
plus the linefeed added by `print`, while the model's subsequent terminal action omits exactly the
answer's final two ASCII spaces. The native completion itself ends immediately after the last
non-space answer character and then `<|im_end|>`; its decoded payload equals the preserved parsed
root reply in all five cases. Thus the experiment-scoped strip-disabled hook is working, and these
five errors were generated terminal-copy differences rather than parser stripping. Their official
marker-gated SequenceMatcher similarities range from {min(scores):.9f} to {max(scores):.9f}, but
the frozen primary raw-exact metric correctly remains zero for them.

The sixth failure is retrieval/selection rather than delivery. The question requests the second
email about an object, but the inert generated selector searches for the second *program* about
that object. It has {retrieval['program_selector_exact_context_matches']} exact user-message
matches, raises `requested ordinal is unavailable`, then the repair action reaches the 2,048-token
limit without a completed tool call or final answer. Its parsed root reply is therefore the empty
string. No child calls occurred in any of the six failures.

This sharpens the 10/16 result: checkpoint 32 produced the clean target in 15/16 contexts, then
delivered 10 exactly, lost five solely at answer-significant trailing-space copying, and selected
the wrong request type once. That is evidence of substantial procedure transfer to longer external
contexts, not a claim of broad generalization or learned decomposition. Generated programs were
read as inert strings and never executed by this analyzer.
"""


if __name__ == "__main__":
    value = build()
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "RESULTS.json").write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    (ROOT / "REPORT.md").write_text(report(value))
    print(json.dumps({"status": value["status"], "categories": value["categories"]}, sort_keys=True))
