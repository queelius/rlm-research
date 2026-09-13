"""Recomputed selection and actual native first-pair seam, no model calls."""
from pathlib import Path


def test_selection_excludes_old_pages_without_gold_filter_and_preserves_examples():
    assert (Path(__file__).parent/"study.py").exists(), "fresh panel binding not implemented"
    import hashlib
    import interface
    import study
    previous=study.read(study.PARENT/"PUBLIC_INPUTS.json")
    excluded={row["filename"] for row in previous["contexts"]}
    seen=set();expected=[]
    for row in sorted(study.read(study.DATA),key=lambda r:(hashlib.sha256((study.REV+"\n"+r["id"]).encode()).hexdigest(),r["id"])):
        if row["filename"] in excluded or row["filename"] in seen:continue
        expected.append(row);seen.add(row["filename"])
        if len(expected)==16:break
    actual=study.read(study.INPUTS)
    assert [r["id"] for r in actual["contexts"]]==[r["id"] for r in expected]
    assert len(seen)==16 and not seen&excluded
    host={r["id"]:r for r in study.read(study.HOST)["contexts"]}
    with study.aliases({"study":study},study.PRIOR):old=study.load("fresh_test_prior_interface",study.PRIOR/"interface.py")
    for index,(row,context) in enumerate(zip(expected,actual["contexts"],strict=True)):
        public={"question":row["qa"]["question"],"pre_text":row["pre_text"],"post_text":row["post_text"],"table":row["table"]}
        assert context["public"]==public and host[row["id"]]["exe_ans"]==row["qa"]["exe_ans"]
        calls=[c for c in actual["calls"] if c["context_index"]==index]
        assert len(calls)==2 and {c["seed"] for c in calls}=={202609300000+index}
        for call in calls:
            assert call["max_tokens"]==384
            assert actual["prompts"][study.call_id(call)]==old.prompt(public,call["kind"])==interface.prompt(public,call["kind"])


def test_actual_fresh_native_pair_and_owner_binding(tmp_path,monkeypatch):
    import study
    fixture=study.load("fresh_reused_native_fixture",study.PRIOR/"test_interface.py")
    fixture.test_actual_first_pair_http_and_inherited_entrypoint(tmp_path,monkeypatch)
