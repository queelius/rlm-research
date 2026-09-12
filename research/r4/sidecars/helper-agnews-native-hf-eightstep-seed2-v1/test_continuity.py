"""Execute the unchanged real two-step HF/Adam/RNG/gradient fixture locally."""
from pathlib import Path


def test_replica_real_two_step_checkpoint_and_no_step_gate(tmp_path):
    assert Path(__file__).with_name("train_step.py").exists(), "replica numeric binding missing"
    import reuse
    scope = {"__name__": "replica_real_continuity_fixture", "__file__": __file__}
    reuse.execute("test_continuity.py", scope)
    scope["test_two_actual_updates_equal_after_adapter_adam_rng_save_reload"](tmp_path)
