"""Load the unchanged trainer against the corrected V2 diagnostic study."""

import importlib.util
import sys

import sft_study_v2 as study


previous = sys.modules.get("sft_study")
sys.modules["sft_study"] = study
try:
    spec = importlib.util.spec_from_file_location("ag_sft_v2_bound_trainer", study.ROOT / "train_sft_v2_source.py")
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
finally:
    if previous is None:
        sys.modules.pop("sft_study", None)
    else:
        sys.modules["sft_study"] = previous

collate = source.collate
make_optimizer = source.make_optimizer
validate_optimizer = source.validate_optimizer
run = source.run
main = source.main


if __name__ == "__main__":
    main()
