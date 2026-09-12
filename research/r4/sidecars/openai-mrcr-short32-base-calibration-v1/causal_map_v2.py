"""Exact native-response to trace-node mapping for the additive short32 repair."""

from __future__ import annotations

import hashlib
import json
import math


def _digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _node(nodes, index):
    if not isinstance(index, int) or index < 0 or index >= len(nodes):
        raise ValueError("invalid trace node index")
    return nodes[index]


def node_evidence(nodes, index):
    """Reconstruct the exact causal prompt/action and role of one sampled node."""
    chain = []
    seen = set()
    cursor = index
    while cursor is not None:
        if cursor in seen:
            raise ValueError("cycle in trace parent chain")
        seen.add(cursor)
        current = _node(nodes, cursor)
        chain.append(cursor)
        cursor = current.get("parent")
    chain.reverse()
    sampled = _node(nodes, index)
    tokens = sampled.get("token_ids") or []
    mask = sampled.get("mask") or []
    if not sampled.get("sampled") or len(tokens) != len(mask):
        raise ValueError("call node is not a well-formed sampled node")
    first_action = next((i for i, selected in enumerate(mask) if selected), len(mask))
    if any(mask[:first_action]) or not all(mask[first_action:]):
        raise ValueError("sample mask is not a single trailing action span")
    prompt = []
    for ancestor in chain[:-1]:
        prompt.extend(_node(nodes, ancestor).get("token_ids") or [])
    prompt.extend(tokens[:first_action])
    action = tokens[first_action:]
    logprobs = sampled.get("logprobs") or []
    if len(logprobs) != len(action) or not all(
        isinstance(value, (int, float)) and math.isfinite(value) for value in logprobs
    ):
        raise ValueError("sample logprobs do not align with the action span")
    # A child's physical parent chain begins at a separate system/user branch whose
    # first sampled node carries subagent_call. A resumed root has subagent_return,
    # never subagent_call, so semantic cross-edges are deliberately not traversed.
    child = any(
        any(parent.get("type") == "subagent_call" for parent in _node(nodes, item).get("semantic_parents", []))
        for item in chain
    )
    return {
        "node": index,
        "parent_chain": chain,
        "prompt_ids": prompt,
        "completion_ids": action,
        "completion_logprobs": logprobs,
        "role": "child" if child else "root",
        "starts_child_invocation": any(
            parent.get("type") == "subagent_call"
            for parent in sampled.get("semantic_parents", [])
        ),
    }


def _sampling_agrees(call, audit):
    left = call.get("sampling") or {}
    right = audit.get("sampling") or {}
    right_extra = right.get("extra_body") or {}
    keys = ("temperature", "top_p", "top_k", "min_p", "seed", "max_tokens")
    return all(left.get(key) == right.get(key, right_extra.get(key)) for key in keys)


def map_trace(trace, native_rows, max_actions=6):
    """Require a bijection between returned native records and committed calls.

    Provider response IDs and client ACP request IDs are distinct identifiers in
    the real interface, so they are retained but not falsely equated. The bridge is
    exact prompt IDs, completion IDs, logprobs, model, sampling and finish reason.
    """
    trace_id = trace.get("id")
    nodes = trace.get("nodes") or []
    calls = trace.get("calls") or []
    audits = [row for row in native_rows if row.get("session_id") == trace_id]
    returned = [row for row in audits if row.get("status") == "returned"]
    errors = [row for row in audits if row.get("status") == "error"]
    committed = [call for call in calls if call.get("node") is not None]
    ambiguous = [call for call in calls if call.get("node") is None]
    candidates = []
    malformed = []
    for call_index, call in enumerate(committed):
        try:
            evidence = node_evidence(nodes, call["node"])
            candidates.append({"call_index": call_index, "call": call, **evidence})
        except (KeyError, TypeError, ValueError) as exc:
            malformed.append({"call_index": call_index, "reason": str(exc)})
    matches = []
    used = set()
    nonunique = []
    for audit_index, audit in enumerate(returned):
        response = audit.get("response") or {}
        tokens = response.get("tokens") or {}
        possible = []
        for candidate_index, candidate in enumerate(candidates):
            call = candidate["call"]
            if candidate_index in used:
                continue
            if (
                candidate["prompt_ids"] == tokens.get("prompt_ids")
                and candidate["completion_ids"] == tokens.get("completion_ids")
                and candidate["completion_logprobs"] == tokens.get("completion_logprobs")
                and call.get("model") == response.get("model") == audit.get("model")
                and call.get("finish_reason") == response.get("finish_reason")
                and _sampling_agrees(call, audit)
                and audit.get("turn", {}).get("trace_id") == trace_id
                and audit.get("evidence", {}).get("completion_ids_sha256")
                == _digest(candidate["completion_ids"])
            ):
                possible.append(candidate_index)
        if len(possible) != 1:
            nonunique.append({"audit_index": audit_index, "candidate_count": len(possible)})
            continue
        candidate_index = possible[0]
        used.add(candidate_index)
        candidate = candidates[candidate_index]
        matches.append(
            {
                "audit_index": audit_index,
                "call_index": candidate["call_index"],
                "node": candidate["node"],
                "role": candidate["role"],
                "starts_child_invocation": candidate["starts_child_invocation"],
                "client_request_id": candidate["call"].get("acp", {}).get("request_id"),
                "provider_response_id": audit.get("response", {}).get("id"),
                "prompt_tokens": len(candidate["prompt_ids"]),
                "action_tokens": len(candidate["completion_ids"]),
                "completion_ids_sha256": _digest(candidate["completion_ids"]),
            }
        )
    complete = bool(
        trace_id
        and not errors
        and not ambiguous
        and not malformed
        and not nonunique
        and len(matches) == len(returned) == len(committed)
        and len(used) == len(candidates)
        and len(returned) <= max_actions
    )
    root = sum(match["role"] == "root" for match in matches)
    child = sum(match["role"] == "child" for match in matches)
    invocations = sum(match["starts_child_invocation"] for match in matches)
    return {
        "complete": complete,
        "trace_id": trace_id,
        "audits": len(audits),
        "returned": len(returned),
        "audit_errors": len(errors),
        "committed_calls": len(committed),
        "ambiguous_calls": len(ambiguous),
        "malformed_call_nodes": malformed,
        "nonunique_audit_matches": nonunique,
        "matches": matches,
        "root_actions": root,
        "child_actions": child,
        "child_invocations": invocations,
        "total_actions": len(matches),
        "cap_respected": len(returned) <= max_actions,
        "id_boundary": (
            "client ACP request IDs and provider response IDs are retained separately; "
            "causal identity is established by exact token/logprob/model/sampling evidence"
        ),
    }
