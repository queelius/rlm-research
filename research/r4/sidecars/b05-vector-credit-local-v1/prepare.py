"""Seal candidate-local credit only after the shared native batch qualifies."""

import study


prepare_arm = study.load("vector_local_prepare_arm", study.SHARED / "prepare_arm.py")


if __name__ == "__main__": prepare_arm.prepare(study)

