"""Synthetic interface demonstrations, never FinQA-derived targets/examples."""
import json
import study

FACTS = [
    {"facts":"A fictional quantity starts with12 units, receives8 more, then loses5. The remaining quantity is divided equally among3 boxes.",
     "question":"How many units are in each box?"},
    {"facts":"A fictional collection contains16 tokens, of which4 are blue.",
     "question":"What percentage of the tokens are blue?"}
]
DIRECT = [{"answer":5},{"answer":"25%"}]
PROGRAMS = [{"program":[["add",12,8],["subtract","#0",5],["divide","#1",3]]},
            {"program":[["divide",4,16]]}]


def examples(arm):
    assert arm in ("direct_scalar","restricted_dsl")
    responses=DIRECT if arm=="direct_scalar" else PROGRAMS
    return [{**facts,"response":response} for facts,response in zip(FACTS,responses,strict=True)]


def public_text(public):return json.dumps(public,ensure_ascii=False,separators=(",",":"))


def prompt(public,arm):
    assert set(public)=={"question","pre_text","post_text","table"}
    assert arm in ("direct_scalar","restricted_dsl")
    instruction=study.science.DIRECT if arm=="direct_scalar" else study.science.DSL
    return (study.science.COMMON+instruction+
            "Synthetic demonstrations (not evidence for the actual task). Each response uses the requested representation.\n"+
            public_text(examples(arm))+"\nNow solve the actual task using only its original evidence below. Return only the requested JSON object.\n"+
            public_text(public))
