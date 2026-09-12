"""Seed-only full schedule equality and actual qualified native/mask binding seam."""
from pathlib import Path


def test_seed_only_schedules_and_actual_native_masks_parent_binding(tmp_path):
    assert Path(__file__).with_name("core.py").exists(), "replica source binding missing"
    import core
    import reuse
    assert core.ROOT == Path(__file__).resolve().parent
    assert core.ATTEMPT == core.ROOT / "outputs/attempt-001"
    seeds = set()
    for step in range(1, 9):
        parent = core.initial_parent()
        parent["step"] = step - 1  # Schedule-only fixture; never authenticates a fake continuation.
        view = core.step_view(step, parent=parent)
        assert view.ATTEMPT == core.ATTEMPT / f"step-{step:03d}"
        assert view.SEED == 20260912910000
        old = core.read(core.DATA / f"inputs/step-{step:03d}/REQUESTS.json")
        new = core.read(core.ROOT / f"inputs/step-{step:03d}/REQUESTS.json")
        for index, (before, after) in enumerate(zip(old, new, strict=True)):
            expected = 20260912900000 + (step-1)*128 + index
            assert after["seed"] == after["body"]["sampling_params"]["seed"] == expected
            assert expected != before["seed"] and expected not in seeds
            seeds.add(expected)
            after["seed"] = before["seed"]
            after["body"]["sampling_params"]["seed"] = before["body"]["sampling_params"]["seed"]
            assert after == before
        assert core.sha(view.HOST_GOLD) == core.sha(reuse.PRIOR / f"inputs/step-{step:03d}/HOST_GOLD.json")
    assert len(seeds) == 1024
    scope = {"__name__": "replica_real_native_fixture", "__file__": __file__}
    reuse.execute("test_native.py", scope)
    scope["test_four_key_native_masks_and_exact_parent_weight_binding"](tmp_path)
