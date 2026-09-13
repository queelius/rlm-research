"""Response-joint single-update entrypoint."""

import argparse
from pathlib import Path
import study


trainer = study.load("vector_joint_shared_trainer", study.SHARED / "trainer.py")
preflight = lambda: trainer.preflight(study)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=int, required=True); args = parser.parse_args()
    trainer.run(study, args.output, args.seconds)

