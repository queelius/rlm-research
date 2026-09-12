"""V2 collector overlay: exact V1 campaign with strict outcome-stop taxonomy."""

import argparse
import asyncio
import json
from pathlib import Path

import causal_map_v2
import classify_v2
import collect as base


def inspect_trace(raw, gold, native_rows, censored=False):
    traces = raw.get("traces") or []
    trace = traces[0] if len(traces) == 1 else {}
    trace_errors = [
        *raw.get("errors", []),
        *(error for item in traces for error in item.get("errors", [])),
    ]
    mapping = causal_map_v2.map_trace(trace, native_rows, max_actions=6)
    stopped = "deadline_censored" if censored else trace.get("stop_condition")
    classified = classify_v2.classify_outcome(
        root_reply=trace.get("root_reply"),
        answer=gold["answer"],
        marker=gold["random_string_to_prepend"],
        stop_condition=stopped,
        trace_ok=bool(raw.get("ok") and len(traces) == 1),
        trace_errors=trace_errors,
        returned_root_actions=mapping["root_actions"],
        returned_child_actions=mapping["child_actions"],
        native_mapping_complete=mapping["complete"],
    )
    nodes = trace.get("nodes") or []
    tool_results = [
        str((node.get("message") or {}).get("content") or "")
        for node in nodes
        if (node.get("message") or {}).get("role") == "tool"
    ]
    usage = [
        call.get("usage") or {}
        for call in trace.get("calls") or []
        if call.get("node") is not None
    ]
    root_reply = trace.get("root_reply")
    return {
        **classified,
        "terminal_status": stopped,
        "root_reply": root_reply,
        "root_reply_sha256": base.study.digest(root_reply) if root_reply is not None else None,
        "trace_id": trace.get("id"),
        "error_types": [error.get("type") for error in trace_errors],
        "native_attempts": mapping["audits"],
        "native_returned": mapping["returned"],
        "native_errors": mapping["audit_errors"],
        "trace_call_entries": len(trace.get("calls") or []),
        "trace_committed_calls": mapping["committed_calls"],
        "trace_ambiguous_calls": mapping["ambiguous_calls"],
        "native_mapping_complete": mapping["complete"],
        "causal_mapping": mapping,
        "root_actions_returned": mapping["root_actions"],
        "child_actions_returned": mapping["child_actions"],
        "child_invocations": mapping["child_invocations"],
        "total_actions_returned": mapping["total_actions"],
        "six_total_root_child_cap_respected": mapping["cap_respected"],
        "delegated": mapping["child_invocations"] > 0,
        "action_tokens": sum(match["action_tokens"] for match in mapping["matches"]),
        "prompt_tokens": sum(item.get("prompt_tokens", 0) for item in usage),
        "completion_tokens": sum(item.get("completion_tokens", 0) for item in usage),
        "context_json_mentions_in_tools": sum("context.json" in value for value in tool_results),
    }


async def run(spec_path, endpoint_path, output, deadline):
    original = (base.study.classify_outcome, base.inspect_trace)
    base.study.classify_outcome = classify_v2.classify_outcome
    base.inspect_trace = inspect_trace
    try:
        return await base.run(spec_path, endpoint_path, output, deadline)
    finally:
        base.study.classify_outcome, base.inspect_trace = original


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.spec, args.endpoint, args.output, args.deadline)))
