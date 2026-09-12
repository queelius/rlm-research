"""CPU-only causal root-turn extraction primitives for a conditional MRCR update."""

from collections import defaultdict
import hashlib
import json
import math


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def _depth(node_index, nodes, cache, visiting):
    if node_index in cache:
        return cache[node_index]
    if node_index in visiting:
        raise ValueError("semantic role cycle")
    visiting.add(node_index)
    parents = nodes[node_index].get("semantic_parents") or []
    implied = []
    for edge in parents:
        parent = edge.get("node")
        if not isinstance(parent, int) or parent < 0 or parent >= len(nodes):
            raise ValueError("invalid semantic parent")
        parent_depth = _depth(parent, nodes, cache, visiting)
        kind = edge.get("type")
        if kind == "subagent_call":
            implied.append(parent_depth + 1)
        elif kind == "subagent_return":
            if parent_depth < 1:
                raise ValueError("subagent return from depth zero")
            implied.append(parent_depth - 1)
        elif kind == "continuation":
            implied.append(parent_depth)
        else:
            raise ValueError("unknown semantic edge type")
    depth = implied[0] if implied else 0
    if any(value != depth for value in implied):
        raise ValueError("semantic parents imply inconsistent depths")
    cache[node_index] = depth
    visiting.remove(node_index)
    return depth


def trace_turns(trace):
    nodes = trace.get("nodes") or []
    calls = trace.get("calls") or []
    cache = {}
    turns = []
    for call_index, call in enumerate(calls):
        node_index = call.get("node")
        if not isinstance(node_index, int) or not (0 <= node_index < len(nodes)):
            raise ValueError("call node index invalid")
        node = nodes[node_index]
        if node.get("sampled") is not True:
            raise ValueError("physical call does not map to sampled node")
        chain = []
        seen = set()
        current = node_index
        while current is not None:
            if current in seen or not isinstance(current, int) or not (0 <= current < len(nodes)):
                raise ValueError("invalid causal parent chain")
            seen.add(current)
            chain.append(current)
            current = nodes[current].get("parent")
        chain.reverse()
        ids = node.get("token_ids") or []
        mask = node.get("mask") or []
        old = node.get("logprobs") or []
        if len(ids) != len(mask):
            raise ValueError("node token/mask shape mismatch")
        count = sum(value is True for value in mask)
        if not count or mask != [False] * (len(mask) - count) + [True] * count:
            raise ValueError("sampled mask is not an exact nonempty suffix")
        if len(old) != count or any(not math.isfinite(value) or value > 0 for value in old):
            raise ValueError("sampled logprobs invalid")
        sequence = [token for index in chain for token in (nodes[index].get("token_ids") or [])]
        prompt = sequence[:-count]
        action = sequence[-count:]
        usage = call.get("usage") or {}
        turns.append(
            {
                "call_index": call_index,
                "node": node_index,
                "depth": _depth(node_index, nodes, cache, set()),
                "causal_chain": chain,
                "prompt_ids": prompt,
                "action_ids": action,
                "input_ids": sequence,
                "labels": [-100] * len(prompt) + action,
                "loss_mask": [0] * len(prompt) + [1] * count,
                "old_logprobs": old,
                "prompt_tokens": len(prompt),
                "action_tokens": count,
                "usage_matches": usage.get("prompt_tokens") == len(prompt)
                and usage.get("completion_tokens") == count,
                "model": call.get("model"),
                "sampling": call.get("sampling"),
                "request_id": (call.get("acp") or {}).get("request_id"),
            }
        )
    if len(turns) != sum(node.get("sampled") is True for node in nodes):
        raise ValueError("sampled-node / physical-call count mismatch")
    return turns


def root_turns(trace):
    return [row for row in trace_turns(trace) if row["depth"] == 0]


def _native_key(prompt, action, logprobs):
    return digest({"prompt_ids": prompt, "action_ids": action, "old_logprobs": logprobs})


def match_native(turns, native_results):
    """One-to-one content matching; filename order and call counts alone are insufficient."""
    buckets = defaultdict(list)
    for index, row in enumerate(native_results):
        tokens = (row.get("response") or {}).get("tokens") or {}
        key = _native_key(
            tokens.get("prompt_ids") or [],
            tokens.get("completion_ids") or [],
            tokens.get("completion_logprobs") or [],
        )
        buckets[key].append(index)
    matched = []
    for turn in turns:
        key = _native_key(turn["prompt_ids"], turn["action_ids"], turn["old_logprobs"])
        choices = buckets[key]
        if len(choices) != 1:
            raise ValueError("root graph/native evidence does not have a unique exact match")
        matched.append({**turn, "native_index": choices.pop()})
    if any(values for values in buckets.values()):
        raise ValueError("unmatched native call evidence remains")
    return matched


def rloo(scores):
    if len(scores) != 4 or any(not isinstance(value, (int, float)) for value in scores):
        raise ValueError("exactly four numeric group rewards required")
    total = sum(scores)
    return [value - (total - value) / 3 for value in scores]
