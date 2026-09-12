"""Reuse exact native raw/mask checks with truthful current-parent metadata."""

import os

import core


def main():
    step = int(os.environ["RLM_AG_EIGHT_STEP"])
    view = core.step_view(step)
    native = core.native_module(view)
    module = core.load_bound(
        f"ag_eight_masks_step_{step}",
        core.SOURCE / "prepare_masks.py",
        {"ag_study": view, "native_collect": native},
    )
    function = core.patched_function(
        module,
        "prepare",
        [
            ('"c32_adapter_sha256"', '"parent_adapter_sha256"'),
            ('"optimizer_steps": 0', '"optimizer_steps": study.STEP - 1'),
            (
                '"schema": "agnews-native-hf-dataset-v1",',
                '"schema": "agnews-eightstep-dataset-v1", '
                '"parent_policy": study.PARENT, "step": study.STEP,',
            ),
        ],
    )
    function()


if __name__ == "__main__":
    main()
