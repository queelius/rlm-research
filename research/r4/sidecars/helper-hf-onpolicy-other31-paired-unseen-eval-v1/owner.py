"""Run one authenticated paired step-1 branch on the frozen unseen256 panel."""

import argparse
import importlib.util
import json
import sys

import paired_eval_study as study


def build(branch):
    study.select(branch)
    source = study.C32_EVAL / "owner.py"
    spec = importlib.util.spec_from_file_location("other31_paired_unseen_collector", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen unseen collector")
    collector = importlib.util.module_from_spec(spec)
    previous = sys.modules.get("unseen_panel_study")
    sys.modules["unseen_panel_study"] = study
    try:
        spec.loader.exec_module(collector)
    finally:
        if previous is None:
            sys.modules.pop("unseen_panel_study", None)
        else:
            sys.modules["unseen_panel_study"] = previous
    original = collector.summarize

    def summarize(calls, gold, expected=True):
        result = original(calls, gold, expected)
        eligibility_path = study.ATTEMPT / "ELIGIBILITY.json"
        eligibility = study.read(eligibility_path)
        result.update(
            schema="helper-hf-other31-paired-unseen-result-v1",
            policy="authenticated paired step-1 child checkpoint",
            branch=eligibility["branch"],
            baseline=eligibility["baseline"],
            primary_step=1,
            training_ready_identity=eligibility["training_ready_identity"],
            training_result_sha256=eligibility["training_result_sha256"],
            shared_collection_sha256=eligibility["shared_collection_sha256"],
            eligibility_sha256=study.sha(eligibility_path),
            schedule_sha256=study.digest(study.schedule()),
            comparison_pair=["rloo", "other31"],
            selection="none; exact sealed branch",
        )
        return result

    collector.summarize = summarize
    return collector


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "qualify", "run"))
    parser.add_argument("--branch", choices=tuple(study.ARMS), required=True)
    parser.add_argument("--outer-seconds", type=int, default=study.CAP)
    arguments = parser.parse_args()
    if arguments.command == "verify":
        print(study.verify(arguments.branch)["identity"])
    elif arguments.command == "qualify":
        print(json.dumps(study.qualify_pair(arguments.branch), sort_keys=True))
    else:
        study.verify(arguments.branch)
        terminal = build(arguments.branch).execute(arguments.outer_seconds)
        print(json.dumps(terminal, sort_keys=True))
        raise SystemExit(0 if terminal["complete"] else 1)
