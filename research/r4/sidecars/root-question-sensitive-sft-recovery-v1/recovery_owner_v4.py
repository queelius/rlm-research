"""V4 owner callback fix; all subprocesses retain the coherent V3 science identity."""
import argparse
from pathlib import Path
import types
import recovery_study_v3 as s
import recovery_binding_v3 as b
from recovery_owner_v3 import protected_deadline, cost_ledger


def _implementation():
    source_path = s.SOURCE_ROOT / "recovery_owner.py"; source = source_path.read_text()
    edits = {
        "study": ("import recovery_study as s", "import recovery_study_v3 as s", 1),
        "binding": ("import recovery_binding as b", "import recovery_binding_v3 as b", 1),
        "capture_entry": ('_command_argv("recovery_collect.py"', '_command_argv("recovery_collect_v3.py"', 1),
        "train_entry": ('s.SOURCE_ROOT / "recovery_train.py"', 's.SOURCE_ROOT / "recovery_train_v3.py"', 1),
        "readout_entry": ('_command_argv("recovery_readout.py"', '_command_argv("recovery_readout_v3.py"', 2),
        "service_status": ("body(stage, end - 90)", "body(stage, end - 90, status)", 1),
        "capture_status": ("def capture(stage, end):", "def capture(stage, end, service_status):", 1),
        "readout_status": ("def readout(stage, end):", "def readout(stage, end, service_status):", 1),
        "dev_start": ("dev_end = min(time.time() + 150, end)", "dev_started = time.time(); dev_end = min(dev_started + 150, end)", 1),
        "dev_call": ('alarm(dev_end); suite.command(stage, "dev8", argv, remaining(dev_end), dev_end)',
            'try:\n                        alarm(dev_end); suite.command(stage, "dev8", argv, remaining(dev_end), dev_end)\n                    except Exception as caught:\n                        errors.append({"stage": "sft6-dev", **error(caught)})', 1),
        "protected_clock": ("protected_end = min(end, time.time() + 1860)",
            "dev_elapsed = time.time() - dev_started\n                    protected_end = protected_deadline(service_status[\"started_epoch\"], dev_elapsed, end)", 1),
    }
    for name, (old, new, expected) in edits.items():
        if source.count(old) != expected: raise ValueError("V4 counted owner edit " + name)
        source = source.replace(old, new)
    module = types.ModuleType("qs_recovery_owner_v4_composed"); module.__file__ = str(source_path)
    module.__dict__["protected_deadline"] = protected_deadline
    exec(compile(source, str(source_path) + "::v4", "exec"), module.__dict__)
    module.cost_ledger = cost_ledger
    return module


implementation = _implementation()


def verify_amendment():
    ready = s.read(s.SOURCE_ROOT / "READY_v4.json")
    if s.digest({k: value for k, value in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("READY_v4 identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if s.sha(path) != pin: raise ValueError("READY_v4 changed " + path)
    return s.verify()


def execute(output):
    verify_amendment()
    return implementation.execute(output)


def parse_args():
    ap = argparse.ArgumentParser(); ap.add_argument("command", choices=("run", "verify"));
    ap.add_argument("--output", type=Path, default=s.ATTEMPT); return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify": print(verify_amendment()["identity"])
    else:
        result = execute(args.output); print({"complete": result["complete"], "error": result["error"]})
        raise SystemExit(0 if result["complete"] else 1)

