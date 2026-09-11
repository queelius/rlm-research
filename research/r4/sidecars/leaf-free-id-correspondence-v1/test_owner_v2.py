import owner_v2


def test_v2_launch_routes_amended_driver_and_caps_collection_from_its_start():
    source = owner_v2.source_text()

    assert 's.ROOT / "driver_v2.py"' in source
    assert "collection_deadline = min(work_deadline, time.time() + 1500)" in source
    assert '"--deadline", str(collection_deadline)' in source
    assert 's.ROOT / "READY_V2.json"' in source

