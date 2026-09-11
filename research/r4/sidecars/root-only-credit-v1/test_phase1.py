"""Focused partition, routing and physical causal-credit regressions."""

import copy
import importlib.util

import pytest


def required(name):
    assert importlib.util.find_spec(name) is not None, f"missing Phase1 implementation: {name}"
    return __import__(name)


def test_fresh_context_groups_are_order_independent_and_gold_is_separate():
    data = required("credit_data")
    rows = [{"group_id": f"group-{i}", "question": f"Question {i}?", "gold": "human being", "coarse": "HUM"} for i in range(400)]
    public, gold, plan = data.build(rows)
    assert (public, gold, plan) == data.build(list(reversed(rows)))
    assert len(public["contexts"]) == 6 and len(plan) == 40
    assert sum(r["split"] == "training" for r in plan) == 32
    assert sum(r["split"] == "validation" for r in plan) == 8
    groups = [g for c in public["contexts"] for g in c["group_ids"]]
    assert len(groups) == len(set(groups)) == 384
    assert all("records" not in c and "gold" not in c for c in public["contexts"])
    assert all("answer" not in t for t in public["tasks"])
    assert all(gold[t["name"]]["answer"] == ("[64]" if t["label"] == "human being" else "[0]") for t in public["tasks"])


def test_native_role_changes_actual_model_only_and_requires_trusted_depth():
    routing = required("native_routing")
    body = {"model": "root", "messages": [{"role": "user", "content": "x"}], "temperature": 0.5}
    before = copy.deepcopy(body)
    headers = {"x-rlm-role-depth": "1", "x-rlm-role-invocation": "child-1", "x-rlm-role-request-id": "a" * 32, "x-rlm-role-kind": "ordinary"}
    audit = routing.route_native(body, headers, {"root": "root", "children": ["child"]}, "child")
    assert body == {**before, "model": "child"} and audit["depth"] == 1
    with pytest.raises(ValueError):
        routing.route_native(copy.deepcopy(before), {}, {"root": "root", "children": ["child"]}, "child")


def test_root_credit_masks_prior_root_and_child_actions_without_changing_aliases():
    exporter = required("root_export")
    from verifiers.v1.graph import MessageNode
    from verifiers.v1.trace import ModelCall, WireTrace
    from verifiers.v1.types import Sampling, Usage
    nodes = [
        MessageNode(message={"role": "user", "content": "x"}, token_ids=[10, 11], mask=[False, False]),
        MessageNode(message={"role": "assistant", "content": "r1"}, parent=0, token_ids=[12, 13], mask=[False, True], sampled=True, logprobs=[-0.2]),
        MessageNode(message={"role": "assistant", "content": "child"}, parent=1, token_ids=[14, 15], mask=[False, True], sampled=True, logprobs=[-0.3]),
        MessageNode(message={"role": "assistant", "content": "r2"}, parent=2, token_ids=[16, 17], mask=[False, True], sampled=True, logprobs=[-0.4]),
    ]
    calls = [ModelCall(node=i, model=model, sampling=Sampling(temperature=0.5, top_p=1, top_k=-1, min_p=0), usage=Usage(prompt_tokens=prompt, completion_tokens=1)) for i, model, prompt in [(1, "root", 3), (2, "child", 5), (3, "root", 7)]]
    trace = WireTrace.model_construct(id="fixture", nodes=nodes, calls=calls)
    roles = {1: {"depth": 0, "actual_alias": "root"}, 2: {"depth": 1, "actual_alias": "child"}, 3: {"depth": 0, "actual_alias": "root"}}
    turns, evidence = exporter.causal_root_turns(trace, roles, root_alias="root", child_alias="child")
    assert len(turns) == 2 and len(evidence) == 3
    assert turns[1]["input_ids"] == [10, 11, 12, 13, 14, 15, 16, 17]
    assert turns[1]["labels"] == [-100] * 7 + [17]
    assert turns[1]["old_logprobs"] == [-0.4]
    assert [call.model for call in trace.calls] == ["root", "child", "root"]
    roles[2]["actual_alias"] = "root"
    with pytest.raises(ValueError):
        exporter.causal_root_turns(trace, roles, root_alias="root", child_alias="child")


def test_infrastructure_failure_is_not_a_negative_reward():
    exporter = required("root_export")
    assert exporter.admitted_reward(False, True, 0, True) is None
    assert exporter.admitted_reward(True, False, 0, True) is None
    assert exporter.admitted_reward(True, True, 0, True) == 0
    assert exporter.admitted_reward(True, True, 1, True) == 1
    assert exporter.admitted_reward(True, True, 1, False) is None
