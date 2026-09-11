"""Focused contract checks: no provider or GPU calls."""
import asyncio
import importlib
import json
import time
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


def module():
    assert (ROOT / "study.py").exists(), "padding control implementation absent"
    return importlib.import_module("study")


def test_grid_preserves_selected_sources_and_balances_dispatch_without_gold_selection():
    s = module()
    source = s.read(s.GRAMMAR / "DATA.json")
    selected = s.select_data(source)
    expected = [c for c in source["contexts"] if c["dataset"] == "trec"][:4]
    expected += [c for c in source["contexts"] if c["dataset"] == "sst2"]
    assert [c["records"] for c in selected["contexts"]] == [c["records"] for c in expected]
    altered = deepcopy(source)
    for c in altered["contexts"]:
        for r in c["records"]:
            r["gold_label"] = "HOST_GOLD_SENTINEL"
    assert [c["source_context_id"] for c in s.select_data(altered)["contexts"]] == [c["source_context_id"] for c in expected]
    d = s.build_design(selected)
    assert len(d["plan"]) == len({r["id"] for r in d["plan"]}) == 128
    assert Counter(r["dataset"] for r in d["plan"]) == {"trec": 64, "sst2": 64}
    assert Counter((r["arm"], r["grammar"]) for r in d["plan"]) == {
        (arm, mode): 16 for arm in ["anonymous", "indexed", "meaningful_tag", "placeholder_tag"] for mode in ["free", "exact"]}
    for arm in s.ARMS:
        for mode in ["free", "exact"]:
            assert Counter(r["cell_order"] for r in d["plan"] if (r["arm"], r["grammar"]) == (arm, mode)) == dict.fromkeys(range(8), 2)


def test_requests_have_common_inputs_and_format_pairs_differ_only_in_schema():
    s = module()
    d = s.build_design(s.load_data())
    altered = deepcopy(d)
    for b in altered["batches"]:
        for r in b["gold"]["records"]:
            r["gold_label"] = "HOST_GOLD_SENTINEL"
    grouped = {}
    for row in d["plan"]:
        body = s.make_request(d, row)
        assert body == s.make_request(altered, row)
        assert body["max_tokens"] == 3072 and body["temperature"] == .5
        assert "gold_label" not in s.serialize(body)
        key = (row["context_index"], row["seed"])
        fixed = (body["messages"][0], body["tools"], body["messages"][1]["content"].split(s.INPUT_MARKER)[1])
        assert key not in grouped or grouped[key] == fixed
        grouped[key] = fixed
        other = s.make_request(d, {**row, "grammar": "exact" if row["grammar"] == "free" else "free"})
        body.pop("structured_outputs", None)
        other.pop("structured_outputs", None)
        assert body == other


@pytest.mark.parametrize("arm", ["meaningful_tag", "placeholder_tag"])
def test_strict_object_arrays_reject_tags_duplicates_cardinality_and_noncanonical_labels(arm):
    s = module()
    gold = {"records": [{"id": "q0001", "gold_label": "negative"}, {"id": "q0002", "gold_label": "positive"}],
            "order": [0, 1], "arm": arm, "labels": ["negative", "positive"]}
    tags = ["q0001", "q0002"] if arm == "meaningful_tag" else ["q0000", "q0000"]
    good = [{"tag": tags[0], "label": "negative"}, {"tag": tags[1], "label": "positive"}]
    scored = s.score_labels(json.dumps(good), gold)
    assert scored["schema_valid"] and scored["strict_correct"] == 2 and scored["aligned_records"] == 2
    bad = [good[:1], good + good[:1], [{**good[0], "tag": "q0099"}, good[1]],
           [{**good[0], "extra": 1}, good[1]], [{**good[0], "label": "POSITIVE"}, good[1]]]
    raw_bad = [json.dumps(v) for v in bad] + [json.dumps(good) + " junk", "null",
        '[{"tag":"q0001","tag":"q0001","label":"negative"},{"tag":"q0002","label":"positive"}]']
    for content in raw_bad:
        score = s.score_labels(content, gold)
        assert not score["schema_valid"]
        assert score["aligned_records"] == 0 and score["predictions"] == [None, None]
    if arm == "meaningful_tag":
        assert not s.score_labels(json.dumps(list(reversed(good))), gold)["schema_valid"]


def test_map_and_anonymous_strictness_and_infrastructure_nulls():
    s = module()
    gold = {"records": [{"id": "q0001", "gold_label": "negative"}, {"id": "q0002", "gold_label": "positive"}],
            "order": [0, 1], "arm": "indexed", "labels": ["negative", "positive"]}
    assert s.score_labels('{"q0002":"positive","q0001":"negative"}', gold)["strict_correct"] == 2
    for text in ['{"q0001":"negative","q0001":"negative","q0002":"positive"}', '{"q0001":"negative","q9999":"positive"}']:
        assert s.score_labels(text, gold)["aligned_records"] == 0
    assert s.score_labels('["negative"]', {**gold, "arm": "anonymous"})["aligned_records"] == 0
    d = s.build_design(s.load_data())
    summary = s.summarize(d, [])
    assert all(r["strict_correct_assignments"] is None and r["strict_full64_correct"] is None for r in summary["coordinates"])
    assert len(summary["paired_context_effects"]) == 32
    assert all(r["meaningful_minus_placeholder_correct"] is None for r in summary["paired_context_effects"])


def test_real_collector_preserves_frozen_wire_and_reports_output_failure_separately(tmp_path):
    s = module()
    assert (ROOT / "driver.py").exists(), "padding collector adapter absent"
    driver = importlib.import_module("driver")
    import httpx
    d = s.build_design(s.load_data())
    d["plan"] = d["plan"][:8]
    d["coordinates"] = deepcopy(d["plan"])
    requests = {r["id"]: s.make_request(d, r) for r in d["plan"]}
    spec = {"design": d, "requests": requests, "request_sha256": {k: s.digest(v) for k, v in requests.items()}}
    async def provider(request):
        body = json.loads(request.content)
        rid = next(k for k, v in requests.items() if v == body)
        row = next(r for r in d["plan"] if r["id"] == rid)
        gold = d["batches"][row["batch_id"]]["gold"]
        result = s.synthetic_output(gold["records"], row["arm"], gold["records"][0]["gold_label"])
        content = json.dumps(result) if row["arm"] != "placeholder_tag" else "[]"
        return httpx.Response(200, json={"id": rid, "model": body["model"], "prompt_token_ids": [1],
            "choices": [{"message": {"content": content}, "finish_reason": "stop", "token_ids": [2]}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1}})
    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider), event_hooks={"request": [driver.wire_hook(spec, tmp_path)]}) as client:
            return await s.collect_calls(client, "http://fake/v1", spec, tmp_path, time.monotonic() + 30)
    records, reason = asyncio.run(go())
    assert reason is None and len(records) == 8
    assert len(list((tmp_path / "wire").glob("*.json"))) == 8
    summary = s.summarize(d, records)
    invalid = [r for r in summary["coordinates"] if r["coordinate"]["arm"] == "placeholder_tag"]
    assert all(r["infrastructure_errors"] == 0 and r["strict_correct_assignments"] == 0 and r["aligned_records"] == 0 for r in invalid)
    assert all(not r["capture"]["tools_executed"] for r in records)
