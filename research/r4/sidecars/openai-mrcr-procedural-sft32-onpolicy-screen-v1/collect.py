"""Grouped collector with raw token evidence under terminal-strip-disabled."""

from __future__ import annotations

import ast
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import checkpoint
import study


def _load_source():
    path = study.SOURCE_EVAL / "collect.py"
    text = path.read_text()
    needle = 'for phase in ("train", "held"):'
    if text.count(needle) != 1:
        raise ValueError("proven collector phase loop changed")
    text = text.replace(needle, 'for phase in ("train",):')
    previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
    sys.modules["study"] = study
    sys.modules["checkpoint"] = checkpoint
    try:
        spec = importlib.util.spec_from_loader("sft32_onpolicy_collect_source", loader=None)
        module = importlib.util.module_from_spec(spec)
        module.__file__ = str(path)
        exec(compile(text, str(path), "exec"), module.__dict__)
        return module
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


source = _load_source()
hooks = study.terminal_hooks()
source_module = lambda: source
role_hooks = source.role_hooks
model_context = source.model_context
native_checkpoints = source.native_checkpoints
validate_native_response = source.validate_native_response


def verify_ready() -> dict:
    ready = study.read(study.READY)
    if ready.get("identity") != study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("screen READY identity changed")
    if ready.get("terminal_condition", {}).get("name") != "terminal-strip-disabled":
        raise ValueError("screen requires the exact terminal-strip-disabled condition")
    for raw, expected in ready.get("closure_sha256", {}).items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("screen closure changed: " + raw)
    if study.digest(study.schedule("train")) != ready["inputs"]["train"]["schedule_sha256"]:
        raise ValueError("screen schedule changed")
    return ready


source.verify_ready = verify_ready


def _tool_messages(trace: dict) -> list[str]:
    values = []
    for node in trace.get("nodes") or []:
        message = node.get("message") or {}
        if message.get("role") == "tool" and isinstance(message.get("content"), str):
            values.append(message["content"])
    return values


def _first_program(trace: dict) -> dict:
    for node in trace.get("nodes") or []:
        message = node.get("message") or {}
        if message.get("role") != "assistant":
            continue
        for call in message.get("tool_calls") or []:
            name = call.get("name") or (call.get("function") or {}).get("name")
            raw_arguments = call.get("arguments") or (call.get("function") or {}).get("arguments")
            if name != "ipython" or not isinstance(raw_arguments, str):
                continue
            try:
                arguments = json.loads(raw_arguments)
                code = arguments.get("code")
            except (TypeError, json.JSONDecodeError):
                code = None
            value = {
                "present": isinstance(code, str),
                "characters": len(code) if isinstance(code, str) else None,
                "sha256": hashlib.sha256(code.encode()).hexdigest() if isinstance(code, str) else None,
                "ast_parseable": False,
                "reads_context_json": False,
            }
            if isinstance(code, str):
                try:
                    tree = ast.parse(code)
                    value["ast_parseable"] = True
                    value["reads_context_json"] = any(
                        isinstance(item, ast.Constant) and item.value == "/context.json"
                        for item in ast.walk(tree)
                    )
                except SyntaxError:
                    pass
            return value
    return {
        "present": False,
        "characters": None,
        "sha256": None,
        "ast_parseable": False,
        "reads_context_json": False,
    }


@functools.lru_cache(maxsize=1)
def raw_tokenizer():
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(str(study.BASE), local_files_only=True)


def mechanism_diagnostics(raw, native_rows, mapping, gold, tokenizer=None):
    tokenizer = tokenizer or raw_tokenizer()
    traces = raw.get("traces") or []
    trace = traces[0] if len(traces) == 1 else {}
    stdout = _tool_messages(trace)
    first_stdout = stdout[0] if stdout else None
    returned = [
        row
        for row in native_rows
        if row.get("session_id") == trace.get("id") and row.get("status") == "returned"
    ]
    root_matches = sorted(
        (row for row in mapping.get("matches", []) if row.get("role") == "root"),
        key=lambda row: row["audit_index"],
    )
    root_evidence = []
    for position, match in enumerate(root_matches):
        if match["audit_index"] >= len(returned):
            continue
        native = returned[match["audit_index"]]
        response = native.get("response") or {}
        tokens = response.get("tokens") or {}
        action = tokens.get("completion_ids") or []
        logs = tokens.get("completion_logprobs") or []
        root_evidence.append(
            {
                "audit_index": match["audit_index"],
                "native_index": native.get("index"),
                "provider_response_id": response.get("id"),
                "model": native.get("model"),
                "prompt_ids": tokens.get("prompt_ids") or [],
                "action_ids": action,
                "old_logprobs": logs,
                "sampling": native.get("sampling"),
                "finish_reason": response.get("finish_reason"),
                "terminal_root_action": position == len(root_matches) - 1,
                "completion_ids_sha256": study.digest(action),
            }
        )

    terminal = root_evidence[-1] if root_evidence else None
    action = terminal["action_ids"] if terminal else []
    decoded_true = tokenizer.decode(action, skip_special_tokens=True) if action else None
    decoded_false = tokenizer.decode(action, skip_special_tokens=False) if action else None
    trace_final = trace.get("root_reply")
    answer = gold["answer"]
    first_stdout_value = {
        "present": first_stdout is not None,
        "characters": len(first_stdout) if first_stdout is not None else None,
        "utf8_bytes": len(first_stdout.encode()) if first_stdout is not None else None,
        "sha256": hashlib.sha256(first_stdout.encode()).hexdigest() if first_stdout is not None else None,
        "traceback_present": "Traceback" in first_stdout if first_stdout is not None else False,
        "truncation_warning_present": first_stdout.startswith("Warning: truncated output") if first_stdout is not None else False,
        "equals_gold": first_stdout == answer,
        "equals_gold_plus_newline": first_stdout == answer + "\n",
    }
    return {
        "schema": "openai-mrcr-procedural-sft32-onpolicy-mechanism-v1",
        "first_program": _first_program(trace),
        "first_stdout": first_stdout_value,
        "tool_observation_count": len(stdout),
        "tool_observation_utf8_bytes": sum(len(item.encode()) for item in stdout),
        "root_learning_evidence": root_evidence,
        "terminal_transport": {
            "trace_final": trace_final,
            "trace_final_sha256": hashlib.sha256(trace_final.encode()).hexdigest() if isinstance(trace_final, str) else None,
            "raw_decode_skip_special_true": decoded_true,
            "raw_decode_skip_special_false": decoded_false,
            "raw_decode_skip_special_true_sha256": hashlib.sha256(decoded_true.encode()).hexdigest() if isinstance(decoded_true, str) else None,
            "raw_decode_skip_special_false_sha256": hashlib.sha256(decoded_false.encode()).hexdigest() if isinstance(decoded_false, str) else None,
            "trace_final_equals_raw_decode_skip_special_true": trace_final == decoded_true,
            "trace_final_equals_gold": trace_final == answer,
            "raw_decode_skip_special_true_equals_gold": decoded_true == answer,
            "raw_decode_skip_special_true_suffix_repr": repr(decoded_true[-80:]) if isinstance(decoded_true, str) else None,
            "parser_contract_status": "terminal-strip-disabled",
        },
    }


original_inspect_trace = source.inspect_trace


def inspect_trace(raw, gold, native_rows, expected_prefix, censored=False):
    value = original_inspect_trace(raw, gold, native_rows, expected_prefix, censored)
    value["mechanism"] = mechanism_diagnostics(
        raw, native_rows, value["causal_mapping"], gold
    )
    value["reward_contract_status"] = "terminal-strip-disabled raw exact primary"
    return value


source.inspect_trace = inspect_trace


def summarize(records, phase, arm):
    value = source._original_summarize(records, phase, arm) if hasattr(source, "_original_summarize") else None
    if value is None:
        value = _original_summarize(records, phase, arm)
    mechanisms = [row["derived"].get("mechanism") for row in records]
    mechanisms = [row for row in mechanisms if row]
    value.update(
        {
            "schema": "openai-mrcr-procedural-sft32-onpolicy-screen-result-v1",
            "reward_contract_status": "terminal-strip-disabled raw exact primary",
            "mechanism_records": len(mechanisms),
            "root_turns_with_native_learning_evidence": sum(
                len(row["root_learning_evidence"]) for row in mechanisms
            ),
            "trace_final_raw_exact_diagnostic": sum(
                row["terminal_transport"]["trace_final_equals_gold"] for row in mechanisms
            ),
            "token_decode_raw_exact_candidate_not_primary": sum(
                row["terminal_transport"]["raw_decode_skip_special_true_equals_gold"]
                for row in mechanisms
            ),
        }
    )
    return value


_original_summarize = source.summarize
source._original_summarize = _original_summarize
source.summarize = summarize


async def run(phase: str, arm: str, endpoint: Path, output: Path, deadline: float) -> int:
    if phase != "train" or arm != "checkpoint32":
        raise ValueError("fixed training-only checkpoint32 screen differs")
    with hooks.installed() as contract:
        code = await source.run(phase, arm, endpoint, output, deadline)
        study.write_x(output / "TERMINAL_STRIP_CONTRACT.json", contract)
        return code


if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("train",), required=True)
    parser.add_argument("--arm", choices=("checkpoint32",), required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.phase, args.arm, args.endpoint, args.output, args.deadline)))
