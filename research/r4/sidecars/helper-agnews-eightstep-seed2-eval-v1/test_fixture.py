"""Reuse real512 denominator fixture and decode one actual prior raw envelope."""
from pathlib import Path


def test_same512_native_raw_and_seed2_parent_gate_interface():
    assert Path(__file__).with_name("bundle.py").exists(), "conditional seed2 evaluator missing"
    import bundle as b
    scope = {"__name__":"seed2_evaluation_fixture"}
    with b.core.original.aliases({"study":b.study,"collect":b.collect,"metrics":b.metrics}):
        exec(compile(b.payload("test_fixture.py"),str(b.SOURCE/"test_fixture.py"),"exec"),scope)
        scope["test_actual_frozen512_schema_native_decode_and_fixed_denominators"]()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(b.study.MODEL,local_files_only=True)
    row = b.study.schedule()[0]
    saved = b.study.read(b.SOURCE/"outputs/c32-001/calls"/(row["call_id"]+".json"))
    raw = b.study.read(saved["raw_response_path"])
    actual = b.collect.decode(row,raw,tokenizer,saved["started_epoch"],saved["ended_epoch"])
    assert actual["prediction"] == saved["prediction"] and actual["completion_ids"] == saved["completion_ids"]
    assert b.study.schedule() == b.old_study.schedule()
    assert b.core.ROOT.name == "helper-agnews-native-hf-eightstep-seed2-v1"
    assert b.study.plan(b.ARM)["same_exposed512"] is True
    assert b.study.attempt(b.ARM).parent == Path(__file__).resolve().parent/"outputs"
    assert b.source_step_gate_text == b.replica_step_gate_text
