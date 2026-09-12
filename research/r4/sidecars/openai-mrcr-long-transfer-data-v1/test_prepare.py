from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_prepare():
    spec = importlib.util.spec_from_file_location("openai_mrcr_long_transfer_prepare", ROOT / "prepare.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_actual_inventory_selects_sixteen_without_relaxing_band_or_disjointness():
    module = load_prepare()
    inventory_rows, pair_incidence = module.load_inventory()
    exposed = module.load_exposed()
    result = module.select_rows(inventory_rows, pair_incidence, exposed)
    assert result["counts"] == {
        "source": 800,
        "band": 102,
        "exposed": 48,
        "eligible_after_exposure_exclusions": 57,
        "selected": 16,
    }
    assert [row["ordinal"] for row in result["selected"]] == [
        121, 117, 189, 103, 134, 106, 149, 101,
        158, 138, 102, 143, 110, 132, 142, 162,
    ]
    assert all(16384 <= row["prompt_plus_answer_o200k"] <= 32768 for row in result["selected"])
    assert module.audit_selected(result["selected"], inventory_rows, pair_incidence, exposed) == []


def test_materialized_rows_preserve_source_bytes_and_keep_gold_private(tmp_path):
    module = load_prepare()
    inventory_rows, pair_incidence = module.load_inventory()
    selected = module.select_rows(inventory_rows, pair_incidence, module.load_exposed())["selected"][:2]
    public, gold = module.materialize(selected, tmp_path)
    assert len(public["records"]) == len(gold) == 2
    for record in public["records"]:
        context = Path(record["prompt_json_path"])
        question = Path(record["final_question_path"])
        assert module.sha(context) == record["prompt_json_sha256"]
        assert module.sha(question) == record["final_question_sha256"]
        assert record["external_file_length_is_not_neural_root_prompt_length"] is True
        assert "answer" not in record and "marker" not in record
    assert all(row["desired_msg_index"] % 2 == 1 for row in gold.values())


def test_hash_ranking_uses_predeclared_namespace_and_not_gold_or_outcomes():
    module = load_prepare()
    row = {"row_sha256": "a" * 64}
    assert module.rank_sha(row) == module.sha_text(module.NAMESPACE + "|" + row["row_sha256"])
    source = (ROOT / "prepare.py").read_text()
    assert "model_output" not in source and "reward" not in source

