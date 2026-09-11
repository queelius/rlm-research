"""Conditional V2 fixed-last readout with the corrected continuation namespace."""
import json

import continuation_readout_owner as base
import continuation_study_v2 as study

base.study = study
base.training.study = study

budget = base.budget
planned_inventory = base.planned_inventory
collector_argv = base.collector_argv
execute = base.execute
parse_args = base.parse_args


if __name__ == "__main__":
    args = parse_args()
    value = study.verify_prepared() if args.command == "verify" else execute(args.output)
    print(json.dumps(value, sort_keys=True, allow_nan=False))
    raise SystemExit(0 if args.command == "verify" or value.get("complete") or value.get("skipped") else 1)
