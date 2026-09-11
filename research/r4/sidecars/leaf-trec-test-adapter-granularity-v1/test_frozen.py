import copy
import json

import protocol
import study


def frozen():
    plan = study.read(study.ROOT / "inputs/PLAN.json")
    bodies = study.read(study.ROOT / "inputs/REQUESTS.json")
    return plan, bodies


def test_exact_148_inventory_and_pair_identity():
    plan, bodies = frozen()
    assert len(plan) == len({row["id"] for row in plan}) == 148
    cells = {}
    for row in plan:
        key = (row["repeat"], row["arm"], row["batch"])
        cells.setdefault(key, {})[row["model_policy"]] = row
    assert len(cells) == 74
    for cell in cells.values():
        assert set(cell) == {"base", "c32"}
        left = copy.deepcopy(bodies[cell["base"]["id"]]); right = copy.deepcopy(bodies[cell["c32"]["id"]])
        assert left.pop("model") == study.BASE_MODEL
        assert right.pop("model") == study.binding()["fixed_child"]
        assert left == right


def test_all_records_covered_once_per_condition_and_last_batches_variable():
    plan, _ = frozen()
    public = study.read(study.ROOT / "inputs/PUBLIC.json")[0]["records"]
    expected = {row["id"] for row in public}
    for seed in study.SEEDS:
        for model in ("base", "c32"):
            for arm in ("W", "S"):
                subset = [row for row in plan if (row["seed"], row["model_policy"], row["arm"]) == (seed, model, arm)]
                actual = [rid for row in subset for rid in row["ids"]]
                assert len(actual) == 500 and len(set(actual)) == 500 and set(actual) == expected
                assert subset[-1]["n"] == (100 if arm == "W" else 4)


def test_native_renderer_authenticates_exact_model_and_tokens():
    plan, bodies = frozen(); coordinate = plan[-1]; body = bodies[coordinate["id"]]
    renderer, tokenizer = study.renderer()
    content = json.dumps({rid: "entity" for rid in coordinate["ids"]}, separators=(",", ":"))
    tokens = tokenizer.encode(content, add_special_tokens=False) + [151645]
    raw = {"model": body["model"], "request_id": "cpu-native-fixture", "choices": [{"token_ids": tokens, "logprobs": {"content": [{"logprob": -1.0} for _ in tokens]}, "finish_reason": "stop"}], "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(tokens)}}
    native = protocol.native(raw, body, renderer)
    assert native["content"] == content and not native["tool_calls"]


def test_seed_scan_has_no_prior_matches():
    scan = study.read(study.ROOT / "inputs/SEED_SCAN.json")
    assert scan["matches_outside_new_sidecar"] == []
    assert scan["started_epoch"] < scan["ended_epoch"]
