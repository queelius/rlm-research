"""Reuse exact512 fixture; distinguish repeated training data from endpoint panel."""
from pathlib import Path


def test_repeated_training_manifest_and_same512_decode_gate_bindings():
    assert Path(__file__).with_name("bundle.py").exists(), "repeated-arm conditional evaluator missing"
    import bundle as b
    scope={"__name__":"repeat128_eval_real_fixture"}
    with b.core.original.aliases({"study":b.study,"collect":b.collect,"metrics":b.metrics}):
        exec(compile(b.payload("test_fixture.py"),str(b.SOURCE/"test_fixture.py"),"exec"),scope)
        scope["test_actual_frozen512_schema_native_decode_and_fixed_denominators"]()
    assert b.study.DATA==b.TRAIN==b.core.DATA
    assert b.study.sha(b.study.DATA/"inputs/MANIFEST.json")=="1f968ef60219a539f8c3bce42cd514426dee38b6b48e1b4a3391b601909bfc1a"
    assert b.study.schedule()==b.old_study.schedule()
    assert b.study.gold()==b.old_study.gold()
    assert b.study.plan(b.ARM)["mechanism_repeat128_vs_broader"] is True
    assert b.source_step_gate_text==b.replica_step_gate_text
