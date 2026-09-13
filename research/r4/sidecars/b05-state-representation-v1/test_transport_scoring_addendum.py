"""Additive coverage for the physical transport-to-metrics boundary."""

import json

import metrics
import owner
import test_screen


def test_existing_http_fixture_is_transport_valid_and_semantically_scored(tmp_path):
    test_screen.test_actual_native_http_path_for_all_three_views(tmp_path)
    records = [json.loads(path.read_text()) for path in sorted((tmp_path / "calls").glob("*.json"))]
    assert len(records) == 3
    assert all(record["transport_valid"] for record in records)
    assert all(record["status"] == "returned_valid" for record in records)

    result = metrics.summarize(tmp_path, qualified=True)
    assert result["available"] == 3
    assert result["unknown"] == 69
    assert not result["complete"]
    for arm in ("raw", "unresolved", "resolved"):
        assert result["arms"][arm]["available"] == 1
        assert result["arms"][arm]["unknown"] == 23
        assert result["arms"][arm]["semantic_valid"] == 1
        row = next(row for row in result["rows"] if row["arm"] == arm and row["available"])
        assert row["ids"] == []
        assert row["semantic_valid"]
    module = owner.implementation()
    assert module.study is owner.study
    assert module.collect is owner.collect
    assert module.metrics is owner.metrics

