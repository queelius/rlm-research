"""V3 owner: coherent entries, exact original readout clocks, qualified usage."""
import argparse
from pathlib import Path
import types
import recovery_study_v3 as s
import recovery_binding_v3 as b


def protected_deadline(stage_started, dev_elapsed, end):
    return min(end, stage_started + 1950 + dev_elapsed - 90)


def _qualified_usage(records):
    old = s.load("qs_recovery_v3_qualified_usage", s.CT / "ct_owner.py",
        s.base.ss.ct_ready["source_sha256"][str(s.CT / "ct_owner.py")], {"ct_study": s.base.ss.ct})
    return old.usage(records)


def cost_ledger(output):
    groups = {
        "original_partial_capture": sorted((s.ORIGINAL_ATTEMPT / "capture").glob("*/physical/*.json")),
        "original_unchanged_baseline": sorted((s.ORIGINAL_ATTEMPT / "unchanged").glob("*/*/physical/*.json")),
        "recovery_missing_capture": sorted((output / "capture").glob("*/physical/*.json")),
        "recovery_sft6_readout": sorted((output / "sft6").glob("*/*/physical/*.json")),
    }
    def tally(paths):
        rows = [s.read(path) for path in paths]; actual = [row for row in rows if row.get("physical_request_attempt")]
        responses = [row for row in actual if isinstance(row.get("response"), dict)]
        choices = [row for row in responses if row["response"].get("choices")]
        return {"all_transport_records": len(rows), "physical_requests_attempted": len(actual),
            "http_responses_returned": sum(isinstance(row.get("response"), dict) or isinstance(row.get("status"), int) for row in actual),
            "choice_bearing_completions": len(choices), "usage": _qualified_usage(actual),
            "files_sha256": {str(path): s.sha(path) for path in paths}}
    return {"by_stage": {name: tally(paths) for name, paths in groups.items()},
        "original_partial_failure_charged": True, "baseline_not_rerun": True,
        "authored_transport_is_not_model_generation": True, "billing": "unknown/not measured"}


def _implementation():
    source_path = s.SOURCE_ROOT / "recovery_owner.py"; source = source_path.read_text()
    edits = {
        "study": ("import recovery_study as s", "import recovery_study_v3 as s"),
        "binding": ("import recovery_binding as b", "import recovery_binding_v3 as b"),
        "capture_entry": ('_command_argv("recovery_collect.py"', '_command_argv("recovery_collect_v3.py"'),
        "train_entry": ('s.SOURCE_ROOT / "recovery_train.py"', 's.SOURCE_ROOT / "recovery_train_v3.py"'),
        "readout_entry": ('_command_argv("recovery_readout.py"', '_command_argv("recovery_readout_v3.py"'),
        "dev_start": ("dev_end = min(time.time() + 150, end)", "dev_started = time.time(); dev_end = min(dev_started + 150, end)"),
        "dev_call": ('alarm(dev_end); suite.command(stage, "dev8", argv, remaining(dev_end), dev_end)',
            'try:\n                        alarm(dev_end); suite.command(stage, "dev8", argv, remaining(dev_end), dev_end)\n                    except Exception as caught:\n                        errors.append({"stage": "sft6-dev", **error(caught)})'),
        "protected_clock": ("protected_end = min(end, time.time() + 1860)",
            "dev_elapsed = time.time() - dev_started\n                    protected_end = protected_deadline(status[\"started_epoch\"], dev_elapsed, end)"),
    }
    for name, (old, new) in edits.items():
        expected = 2 if name == "readout_entry" else 1
        if source.count(old) != expected: raise ValueError("V3 counted owner edit " + name)
        source = source.replace(old, new)
    module = types.ModuleType("qs_recovery_owner_v3_composed"); module.__file__ = str(source_path)
    module.__dict__["protected_deadline"] = protected_deadline
    exec(compile(source, str(source_path) + "::v3", "exec"), module.__dict__)
    module.cost_ledger = cost_ledger
    return module


implementation = _implementation()
execute = implementation.execute


def parse_args():
    ap = argparse.ArgumentParser(); ap.add_argument("command", choices=("run", "verify"));
    ap.add_argument("--output", type=Path, default=s.ATTEMPT); return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify": print(s.verify()["identity"])
    else:
        result = execute(args.output); print({"complete": result["complete"], "error": result["error"]})
        raise SystemExit(0 if result["complete"] else 1)
