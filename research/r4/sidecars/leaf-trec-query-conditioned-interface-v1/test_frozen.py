import copy

import protocol
import study as s


def frozen():
    return s.read(s.ROOT / "inputs/PLAN.json"), s.read(s.ROOT / "inputs/REQUESTS.json")


def test_ready_and_exact_inventory():
    ready = s.verify()
    plan, bodies = frozen()
    assert ready["planned"] == len(plan) == len(bodies) == 192
    assert len({row["id"] for row in plan}) == 192
    assert not s.ATTEMPT.exists()


def test_four_cells_share_seed_records_and_pair_per_block():
    plan, bodies = frozen()
    blocks = {}
    for row in plan:
        blocks.setdefault((row["batch"], row["pair_index"]), []).append(row)
    assert len(blocks) == 48
    for values in blocks.values():
        assert len(values) == 4
        assert len({tuple(row["ids"]) for row in values}) == 1
        assert len({tuple(row["pair"]) for row in values}) == 1
        assert len({row["seed"] for row in values}) == 1
        for interface in ("full6", "abo"):
            cells = {row["model_policy"]: bodies[row["id"]] for row in values if row["interface"] == interface}
            left, right = copy.deepcopy(cells["base"]), copy.deepcopy(cells["c32"])
            left.pop("model")
            right.pop("model")
            assert left == right


def test_exact_schema_and_wire_prompt_pair_visibility():
    plan, bodies = frozen()
    _, tokenizer = s.renderer()
    for row in plan:
        body = bodies[row["id"]]
        schema = body["sampling_params"]["structured_outputs"]["json"]
        allowed = list(protocol.CATEGORIES if row["interface"] == "full6" else protocol.PROJECTED)
        assert schema["required"] == row["ids"]
        assert all(value["enum"] == allowed for value in schema["properties"].values())
        decoded = tokenizer.decode(body["token_ids"])
        assert f"A means {row['pair'][0]}; B means {row['pair'][1]};" in decoded
        assert all(record_id in decoded for record_id in row["ids"])
        assert len(body["token_ids"]) + 2048 <= 8192


def test_seed_catalog_scan_and_provenance():
    scan = s.read(s.ROOT / "inputs/SEED_SCAN.json")
    provenance = s.read(s.ROOT / "inputs/PROVENANCE.json")
    assert scan["started_epoch"] < scan["ended_epoch"]
    assert scan["matches_outside_new_sidecar"] == []
    assert provenance["selection_used_labels"] is False
    assert provenance["optimizer_group_overlap"] == 0
    assert provenance["source_license_status"].startswith("underlying TREC data rights unspecified")
