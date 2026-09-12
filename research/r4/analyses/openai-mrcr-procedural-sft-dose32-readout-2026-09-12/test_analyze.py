"""Focused evidence tests; fixture programs are only parsed as inert text."""

import copy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent


def module():
    path = ROOT / "analyze.py"
    assert path.exists(), "analyzer implementation is absent"
    spec = importlib.util.spec_from_file_location("dose32_analyzer_test", path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_teacher_patterns_do_not_call_a_schema_dump_correct_retrieval():
    a = module()
    teacher = a.read(a.CORPUS)["episodes"][0]["teacher"]["authored_code"]
    good = a.program_features(teacher, teacher)
    assert good["teacher_ast_exact"] and good["role_tests"] and good["successor_index"]
    assert good["ordinal_index"] and not good["broad_document_dump"]
    bad = a.program_features("data = json.load(open('/context.json'))\nprint(data)\nentries = data.get('diary_entries', [])", teacher)
    assert bad["broad_document_dump"] and bad["top_level_dict_assumption"]
    assert not bad["teacher_ast_exact"] and not bad["successor_index"]


def test_program_analysis_never_executes_code(tmp_path):
    a = module()
    sentinel = tmp_path / "must-not-exist"
    code = f"__import__('pathlib').Path({str(sentinel)!r}).write_text('bad')"
    assert a.program_features(code, None)["parseable"]
    assert not sentinel.exists()


def test_actual_checkpoint4_readout_is_train_failure_not_transfer():
    a = module()
    report = a.build_report()
    old = report["stages"]["train_checkpoint4"]
    assert (old["summary"]["recorded"], old["summary"]["available"], old["summary"]["raw_exact"]) == (32, 28, 0)
    assert old["summary"]["first_teacher_ast_exact"] == 0
    assert old["summary"]["any_successor_pattern"] == 0
    assert not old["train_gate"]["eligible"]
    assert all(row["native_initial_prefix_exact"] for row in old["rows"])
    assert not old["integrity_errors"]


def test_pairing_rejects_changed_seed_instead_of_claiming_regression():
    a = module()
    row = {"coordinate_id": "x", "record_id": "r", "context_sha256": "c", "repeat": 0,
           "seed": 1, "available": True, "raw_exact": False, "first_action_sha256": "a",
           "native_initial_prefix_sha256": "p"}
    other = copy.deepcopy(row)
    other["seed"] = 2
    with pytest.raises(ValueError, match="paired coordinate"):
        a.paired([row], [other])
    missing = a.paired([row], [])
    assert missing["matched_coordinates"] == 0 and missing["paired_available"] == 0


def test_native_final_mismatch_is_reported_not_silently_scored():
    a = module()
    evidence = a.native_evidence("trace", "answer", "root", [{"session_id": "trace", "status": "returned",
        "index": 0, "model": "root", "response": {"message": {"role": "assistant", "content": "different"},
        "tokens": {"prompt_ids": [1, 2]}}}], [1, 2])
    assert evidence["native_initial_prefix_exact"]
    assert not evidence["native_final_exact_to_trace"]


def test_unavailable_missing_prefix_remains_unknown_in_paired_report():
    a = module()
    row = {"coordinate_id": "x", "record_id": "r", "context_sha256": "c", "repeat": 0,
           "seed": 1, "available": True, "raw_exact": True, "first_action_sha256": "a",
           "native_initial_prefix_sha256": "p"}
    unknown = {**row, "available": False, "native_initial_prefix_sha256": None}
    pair = a.paired([row], [unknown])
    assert pair["matched_coordinates"] == 1 and pair["paired_available"] == 0
    assert pair["wins_right"] == pair["losses_right"] == 0
    assert pair["pairs"][0]["right_exact"] is None


def test_fixed_binding_rejects_checkpoint4_as_checkpoint32():
    a = module()
    binding = a.read(a.OLD_EVAL / 'outputs/train-readout-001/owned-service/BINDING.json')
    assert callable(getattr(a, 'validate_binding', None)), 'binding qualification is absent'
    assert a.validate_binding(binding, 4).endswith('step4')
    with pytest.raises(ValueError, match='fixed root/child binding'):
        a.validate_binding(binding, 32)


def test_correct_print_then_copy_corruption_is_not_a_wrong_selector():
    a = module()
    assert callable(getattr(a, 'retrieval_copy_evidence', None)), 'retrieval/copy boundary is absent'
    truth = {'answer':'MARKgood\nbody','random_string_to_prepend':'MARK'}
    document = [{'role':'assistant','content':'bad body'}, {'role':'assistant','content':'good\nbody'}]
    result = a.retrieval_copy_evidence(['MARKgood\nbody\n'], 'MARKgood\\nbody', truth, document)
    assert result['clean_correct_target_observed']
    assert result['correct_print_then_nonempty_wrong_final']
    assert result['newline_only_repair_would_match_DIAGNOSTIC_ONLY']
    assert not result['clean_wrong_record_printed']
    wrong = a.retrieval_copy_evidence(['MARKbad body\n'], 'MARKbad body', truth, document)
    assert wrong['clean_wrong_record_printed'] and not wrong['clean_correct_target_observed']
