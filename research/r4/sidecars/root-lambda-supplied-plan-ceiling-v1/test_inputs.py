import study as s


def test_exact_eight_episode_forty_batch_inventory():
    plan = s.read(s.ROOT / "inputs/PLAN.json")
    public = {row["id"]: row for row in s.read(s.ROOT / "inputs/PUBLIC.json")}
    assert len(plan) == 40 and len(public) == 8
    assert {(row["cluster"], row["size"]) for row in public.values()} == {
        (cluster, size) for cluster in range(4) for size in (64, 256)
    }
    for episode in public.values():
        rows = [row for row in plan if row["context_id"] == episode["id"]]
        assert len(rows) == episode["size"] // 32
        assert [identifier for row in rows for identifier in row["ids"]] == [
            record["id"] for record in episode["records"]
        ]


def test_gold_is_absent_from_frozen_native_bodies():
    bodies = s.read(s.ROOT / "inputs/REQUESTS.json")
    gold = s.read(s.ROOT / "inputs/HOST_GOLD.json")
    for row in s.read(s.ROOT / "inputs/PLAN.json"):
        body = bodies[row["id"]]
        assert body["model"] == s.binding()["fixed_child"]
        assert len(body["token_ids"]) + 2048 <= 8192
        assert "gold" not in str(body).lower()
        assert row["context_id"] in gold
