import copy

import prepare
import protocol


def test_selected_panel_and_six_pairs_are_label_blind_and_complete():
    rows, provenance = prepare.selected_rows()
    assert len(rows) == len({row["id"] for row in rows}) == 128
    assert provenance["selection_used_labels"] is False
    assert len(prepare.PAIRS) == 6
    counts = {label: 0 for label in protocol.CATEGORIES}
    for left, right in prepare.PAIRS:
        assert left != right
        counts[left] += 1
        counts[right] += 1
    assert set(counts.values()) == {2}


def test_plan_has_192_four_cell_paired_blocks():
    rows, _ = prepare.selected_rows()
    plan = prepare.plan_only(rows)
    assert len(plan) == len({row["id"] for row in plan}) == 192
    blocks = {}
    for row in plan:
        key = (row["batch"], row["pair_index"])
        blocks.setdefault(key, []).append(row)
    assert len(blocks) == 48
    for values in blocks.values():
        assert len({row["seed"] for row in values}) == 1
        assert {(row["model_policy"], row["interface"]) for row in values} == {
            ("base", "full6"), ("base", "abo"), ("c32", "full6"), ("c32", "abo")
        }
        assert all(row["n"] == 16 for row in values)


def test_scoring_projects_full_labels_without_repair():
    ids = ["x", "y", "z"]
    gold = {"x": "human being", "y": "location", "z": "entity"}
    pair = ("human being", "location")
    full = protocol.score('{"x":"human being","y":"entity","z":"location"}', ids, gold, pair, "full6", True)
    direct = protocol.score('{"x":"A","y":"other","z":"B"}', ids, gold, pair, "abo", True)
    assert full["projected"] == direct["projected"] == {"x": "A", "y": "other", "z": "B"}
    assert full["strict_correct"] == direct["strict_correct"] == 1
    assert full["confusion"]["A"] == {"tp": 1, "fp": 0, "fn": 0}
    assert full["confusion"]["B"] == {"tp": 0, "fp": 1, "fn": 1}


def test_malformed_completed_is_zero_and_missing_is_null():
    malformed = protocol.score("not-json", ["x"], {"x": "entity"}, ("entity", "location"), "abo", True)
    missing = protocol.score(None, ["x"], {"x": "entity"}, ("entity", "location"), "abo", False)
    assert malformed["available"] and malformed["strict_correct"] == 0
    assert not malformed["complete_map"]
    assert not missing["available"] and missing["strict_correct"] is None


def test_bodies_hold_text_pair_seed_and_prompt_constant_within_block():
    rows, _ = prepare.selected_rows()
    plan = prepare.plan_only(rows)
    bodies = prepare.build_bodies(plan, rows, prepare.tokenizer())
    first_block = [row for row in plan if row["batch"] == 0 and row["pair_index"] == 0]
    by_cell = {(row["model_policy"], row["interface"]): bodies[row["id"]] for row in first_block}
    for interface in ("full6", "abo"):
        left = copy.deepcopy(by_cell[("base", interface)])
        right = copy.deepcopy(by_cell[("c32", interface)])
        left.pop("model"); right.pop("model")
        assert left == right
    assert by_cell[("base", "full6")]["sampling_params"]["seed"] == by_cell[("base", "abo")]["sampling_params"]["seed"]
