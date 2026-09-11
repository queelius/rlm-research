"""Owner V2: exact V1 flow with the qualified existing training interpreter."""
import json

import continuation_owner as base
import continuation_study_v2 as study

base.study = study


def trainer_argv(stage, generation, policy, deadline):
    return [str(study.TRAIN), str(study.ROOT / "continuation_train_v2.py"), "--group",
            str(stage / "collection/export/GROUP.json"), "--generation",
            str(stage / "GENERATION.json"), "--checkpoint", str(policy["path"]),
            "--output", str(stage / "training"), "--deadline", str(float(deadline))]


base.trainer_argv = trainer_argv
budget = base.budget
planned_inventory = base.planned_inventory
collector_argv = base.collector_argv
train_window = base.train_window
collect_window = base.collect_window
cost_ledger = base.cost_ledger
execute = base.execute
parse_args = base.parse_args


if __name__ == "__main__":
    args = parse_args()
    value = study.verify_prepared() if args.command == "verify" else execute(args.output)
    print(json.dumps(value, sort_keys=True, allow_nan=False))
    raise SystemExit(0 if args.command == "verify" or value["complete"] else 1)
