"""Exact336/768 schedule, ordered partitions, failure accounting and service seam."""

from collections import Counter


def test_all_three_sizes_cover_each_frozen_record_once_without_changing_wording():
    import size_study as study

    rows = study.make_schedule()
    assert len(rows) == 336
    assert Counter(row["batch_size"] for row in rows) == {16: 16, 4: 64, 1: 256}
    assert sum(len(row["ids"]) for row in rows) == 768
    seen = Counter((row["batch_size"], identifier) for row in rows for identifier in row["ids"])
    assert len(seen) == 768 and set(seen.values()) == {1}
    assert len({row["call_id"] for row in rows}) == 336
    public = study.source().panel()[2]["records"]
    for row in rows:
        records = [{"id": r["id"], "text": r["text"]} for r in public if r["id"] in row["ids"]]
        expected, _ = study.builder().prompt(row["dataset"], records)
        assert row["request_text"] == expected
        params = row["body"]["sampling_params"]
        assert params["temperature"] == 0 and params["max_tokens"] == 1024
        assert list(params["structured_outputs"]["json"]["properties"]) == row["ids"]
        assert params["structured_outputs"]["json"]["required"] == row["ids"]
    for dataset in ("trec", "ag_news"):
        assert (
            len({r["body"]["sampling_params"]["seed"] for r in rows if r["dataset"] == dataset})
            == 1
        )


def test_summary_keeps_wrong_missing_and_unattempted_in_fixed_denominators():
    from owner import summarize

    schedule = [
        {"call_id": "a16", "dataset": "trec", "batch_size": 16, "ids": ["a", "b"]},
        {"call_id": "a4", "dataset": "trec", "batch_size": 4, "ids": ["a", "b"]},
        {"call_id": "a1", "dataset": "trec", "batch_size": 1, "ids": ["a"]},
        {"call_id": "b1", "dataset": "trec", "batch_size": 1, "ids": ["b"]},
    ]
    calls = [
        {**schedule[0], "status": "returned_valid", "prediction": {"a": "entity", "b": "entity"}},
        {**schedule[1], "status": "invalid_response", "prediction": {}},
        {**schedule[2], "status": "returned_valid", "prediction": {"a": "entity"}},
    ]
    result = summarize(calls, schedule, {"labels": {"a": "entity", "b": "location"}})
    sixteen = result["by_dataset_size"]["trec:16"]
    assert sixteen["correct"] == 1 and sixteen["wrong"] == 1 and sixteen["planned_predictions"] == 2
    assert sixteen["usage_unknown_calls"] == 1 and sixteen["total_tokens"] == 0
    assert result["by_dataset_size"]["trec:4"]["invalid_predictions"] == 2
    assert result["by_dataset_size"]["trec:4"]["usage_unknown_calls"] == 1
    singleton = result["by_dataset_size"]["trec:1"]
    assert singleton["unattempted_calls"] == 1 and singleton["unavailable_predictions"] == 1
    assert singleton["correct_lower_bound"] == 1 and singleton["correct_upper_bound"] == 2
    assert result["planned_calls"] == 4 and result["attempted_calls"] == 3
    assert result["planned_predictions"] == 6 and not result["all_calls_attempted"]


def test_real_cpu_dependencies_bind_sealed_v4_launcher_without_a_gpu(monkeypatch):
    import size_study as study

    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-only-placeholder")
    suite = study.dependencies()
    assert suite.SERVE == study.SERVICE
    assert suite.life.ALLOCATION_SERVICE == study.SERVICE
    assert callable(suite.start_service) and callable(suite.release_service)
    assert callable(study.validator().response_record)
