"""Native-environment attempt-002 entry; scientific owner behavior is unchanged from V3."""
import json

import readout_owner as base
import readout_study_v4 as study

# Every inherited owner function resolves its module-global study at call time.
base.study = study

budget = base.budget
collector_argv = base.collector_argv
planned_inventory = base.planned_inventory
dependencies = base.dependencies
cost_ledger = base.cost_ledger
execute = base.execute
parse_args = base.parse_args


if __name__ == "__main__":
    args = parse_args()
    value = study.verify_prepared() if args.command == "verify" else execute(args.output)
    print(json.dumps(value, sort_keys=True))
    raise SystemExit(0 if args.command == "verify" or value.get("complete") or value.get("skipped") else 1)
