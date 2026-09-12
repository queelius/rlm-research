"""Run the matched-three-update reference fixed256 readout."""

import argparse
import importlib.util
import json
import sys

import study


def build():
    spec = importlib.util.spec_from_file_location("reference_step3_collector", study.C32 / "owner.py")
    collector = importlib.util.module_from_spec(spec)
    previous = sys.modules.get("unseen_panel_study"); sys.modules["unseen_panel_study"] = study
    try: spec.loader.exec_module(collector)
    finally:
        if previous is None: sys.modules.pop("unseen_panel_study", None)
        else: sys.modules["unseen_panel_study"] = previous
    original = collector.summarize
    def summarize(calls, gold, expected=True):
        result = original(calls, gold, expected); eligibility = study.read(study.ATTEMPT / "ELIGIBILITY.json")
        result.update(schema="helper-hf-reference-step3-unseen-result-v1",
            policy="reference T1/LR1e-5 matched checkpoint-0003; not fixed-fourstep primary",
            primary_step=None, matched_update_step=3, fixed_fourstep_primary=False,
            training_ready_identity=eligibility["training_ready_identity"],
            checkpoint_state_sha256=eligibility["checkpoint_state_sha256"],
            final_checkpoint_state_sha256=eligibility["final_checkpoint_state_sha256"],
            eligibility_sha256=study.sha(study.ATTEMPT / "ELIGIBILITY.json"),
            schedule_sha256=study.digest(study.schedule()))
        return result
    collector.summarize = summarize; return collector


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("verify", "qualify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=study.CAP); args = parser.parse_args()
    if args.command == "verify": print(study.verify()["identity"])
    elif args.command == "qualify": print(json.dumps(study.qualify(), sort_keys=True))
    else:
        study.verify(); terminal = build().execute(args.outer_seconds); print(json.dumps(terminal, sort_keys=True))
        raise SystemExit(0 if terminal["complete"] else 1)
