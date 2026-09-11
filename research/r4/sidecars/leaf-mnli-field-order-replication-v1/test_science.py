import copy
import hashlib

import protocol as p
import study as s


def test_plan_is_six_by_sixteen_with_fresh_paired_seeds():
    rows = p.plan()
    assert len(rows) == 96
    assert set(p.ARMS) == {f"{r}_{o}" for r in ("wrong", "alien", "aligned") for o in ("tag_first", "label_first")}
    for ci in range(16):
        cells = [r for r in rows if r["context_index"] == ci]
        assert {r["arm"] for r in cells} == set(p.ARMS)
        assert {r["seed"] for r in cells} == {989626101 + ci}
    assert not ({r["seed"] for r in rows} & set(range(982626101, 982626109)))


def test_contexts_are_balanced_and_disjoint_from_named_inventory():
    data = s.read(s.ROOT / "DATA.json")["contexts"]
    audit = s.read(s.ROOT / "SELECTION_AUDIT.json")
    assert len(data) == 16
    assert [sum(c["genre"] == g for c in data) for g in p.GENRES] == [4, 4, 4, 4]
    assert all(len(c["premise_groups"]) == 16 and len(c["records"]) == 48 for c in data)
    selected = {group for c in data for group in c["premise_groups"]}
    assert len(selected) == 256
    assert not selected & set(audit["excluded_premise_groups"])
    assert audit["prior_selected_overlap"] == []
    assert audit["first_ranked_groups_selected"]


def test_selection_is_label_invariant_among_inherited_eligible_groups():
    audit = s.read(s.ROOT / "SELECTION_AUDIT.json")
    assert audit["eligibility_uses_labels"]
    assert audit["ranking_uses_labels"] is False
    assert audit["label_mutation_ranking_invariant"]


def test_field_order_changes_only_instruction_and_object_order():
    context = p.contexts()[0]
    tag = p.request(context, {"arm": "wrong_tag_first", "seed": 1})
    label = p.request(context, {"arm": "wrong_label_first", "seed": 1})
    left = copy.deepcopy(tag); right = copy.deepcopy(label)
    left["messages"][1]["content"] = ""; right["messages"][1]["content"] = ""
    left["structured_outputs"] = {}; right["structured_outputs"] = {}
    assert left == right
    assert p.field_order("wrong_tag_first") == ("tag", "label")
    assert p.field_order("wrong_label_first") == ("label", "tag")


def test_metric_and_gate_are_frozen_at_context_level():
    assert p.PRIMARY == "(wrong_label_first-wrong_tag_first)-(aligned_label_first-aligned_tag_first)"
    assert p.GATE == {"minimum_effect": 0.10, "minimum_positive_contexts": 12, "contexts": 16, "availability_not_lower": True}


def test_all_96_native_prefixes_wires_and_grammars_are_frozen():
    native=s.read(s.ROOT/"CPU_NATIVE.json");prompts=s.read(s.ROOT/"PROMPT_IDS.json")
    wires=s.read(s.ROOT/"ORDERED_REQUESTS.json");plan=s.read(s.ROOT/"PLAN.json")
    assert native["requests"]==native["schemas_compiled"]==len(prompts)==len(wires)==len(plan)==96
    assert len(native["schema_checks"])==96 and native["all_fit8192"]
    assert all(row["correct_order_accepts"] and row["opposite_order_rejected"] for row in native["schema_checks"])
    assert {key:hashlib.sha256(value.encode()).hexdigest() for key,value in wires.items()}==native["request_wire_sha256"]
    assert all(isinstance(value,list) and value and all(type(token)is int for token in value) for value in prompts.values())
