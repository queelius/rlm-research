"""Run the unchanged HF target-score gate over the V2 token-decoded collection."""

import argparse
import importlib.util
import json
from pathlib import Path

import study


_spec = importlib.util.spec_from_file_location(
    "fresh_helper_qualification_v1_qualify", study.V1_ROOT / "qualify.py"
)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
base.study = study

require_service_released = base.require_service_released
result_for_diagnostics = base.result_for_diagnostics
load_v1_modules = base.load_v1_modules
prepare_records = base.prepare_records
run = base.run


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cap-seconds", type=int, required=True)
    parser.add_argument("--service-stopped", type=Path, required=True)
    arguments = parser.parse_args()
    print(
        json.dumps(
            run(
                arguments.output.resolve(),
                arguments.cap_seconds,
                arguments.service_stopped.resolve(),
            )
        )
    )
