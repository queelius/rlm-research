"""Actual facade/collector and narrow reuse-semantics regression."""

import copy

import owner
import paired_eval_study as study
import pytest


def test_actual_both_branch_collectors_and_source_reuse_rejection():
    schedules = []
    for branch in ("rloo", "other31"):
        collector = owner.build(branch)
        assert collector.study is study
        assert study.resolve_branch() == branch
        assert study.ARMS[branch]["attempt"] == study.ATTEMPT
        rows = collector.study.schedule()
        assert len(rows) == 64
        assert len({identifier for row in rows for identifier in row["ids"]}) == 256
        assert all(row["body"]["sampling_params"]["temperature"] == 0 for row in rows)
        schedules.append(rows)
    assert schedules[0] == schedules[1] == study.source_eval().schedule()
    proof = study.read(study.TRAINING / "SOURCE_PROOF.json")
    collection = {
        "freshly_sampled": False,
        "reused_exact_hf_actions": True,
        "fresh_model_calls_in_repair": 0,
        "source_sampling_was_fresh": True,
        "source_reuse": proof,
    }
    study.verify_reuse_header(collection, proof)
    for key, value in (
        ("freshly_sampled", True),
        ("reused_exact_hf_actions", False),
        ("fresh_model_calls_in_repair", 128),
        ("source_sampling_was_fresh", False),
        ("source_reuse", {}),
    ):
        broken = copy.deepcopy(collection)
        broken[key] = value
        with pytest.raises(ValueError, match="reuse"):
            study.verify_reuse_header(broken, proof)
