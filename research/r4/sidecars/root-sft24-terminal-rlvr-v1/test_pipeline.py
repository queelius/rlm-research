from types import SimpleNamespace

import pytest

import warm_collect as collect
import warm_export as export
import warm_metrics as metrics
import warm_study as study
import warm_train as train


def test_collector_plans_exact_eight_windows_and_shared_readout():
    for window in range(1, 9):
        rows = collect.planned(f"window-{window}")
        assert len(rows) == 24 and all(row["context_id"] == f"training-{window-1:02d}" for row in rows)
    assert len(collect.planned("readout-unchanged")) == 48
    assert len(collect.planned("readout-trained")) == 48
    with pytest.raises(ValueError):
        collect.planned("window-9")


def test_qualified_pipeline_sources_and_complete24_admission_contract():
    assert collect.SOURCE_SHA == "8f2901a03657dc6c417260e4350340202a9a3ee738ac8453ce48a3c628654dd7"
    assert export.SOURCE_SHA == "3b0e58ef886720cf2efd578ace0629d04b54463532c0531a443dd7fac3447796"
    assert train.SOURCE_SHA == "a5064c270f80e157945775accde4e57cd9c5f9e82d1bb17862a118786cb13878"
    with pytest.raises(ValueError):
        train.check_members([], study.candidate_plan(1), {"generation_id": "x"})
    assert callable(metrics.endpoint) and callable(export.rebuild)
