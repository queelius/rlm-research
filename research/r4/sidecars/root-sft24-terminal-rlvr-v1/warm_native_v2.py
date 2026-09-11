"""V2 native entry adds the exact authenticated export-replay CLI."""
import json

import warm_native as v1

stack = v1.stack
prompt = v1.prompt
make_task = v1.make_task
first_prefix = v1.first_prefix
interface = v1.interface
exact_turns = v1.exact_turns
validate_typed_audit = v1.validate_typed_audit


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify-export",))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from warm_export_v2 import authenticate_export
    print(json.dumps(authenticate_export(args.output), sort_keys=True))
