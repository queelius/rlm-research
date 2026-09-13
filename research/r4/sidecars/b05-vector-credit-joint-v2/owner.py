"""Finite MAIN-owned V2 response-joint subprocess wrapper."""

import argparse
import study


owner_core = study.load("vector_joint_v2_owner_core", study.SHARED / "owner_core.py")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("action", choices=("verify", "run")); args = parser.parse_args()
    if args.action == "verify":
        import train
        print(train.preflight()[0]["identity"])
    else: raise SystemExit(owner_core.run(study))
