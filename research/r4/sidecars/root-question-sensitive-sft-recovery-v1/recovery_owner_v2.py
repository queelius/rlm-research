"""Additive V2 owner: verified recovered readout binding; science and clocks unchanged."""
import argparse
from pathlib import Path
import recovery_owner as v1
import recovery_study as s
import recovery_binding_v2 as b


def verify_v2():
    ready = s.read(s.SOURCE_ROOT / "READY_v2.json")
    if s.digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("READY_v2 identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if s.sha(path) != pin: raise ValueError("READY_v2 changed " + path)
    s.capture_boundary(); s.starting_policy(); return ready


def execute(output):
    original_verify = s.verify; original_argv = v1._command_argv; original_b = v1.b
    s.verify = verify_v2; v1.b = b
    v1._command_argv = lambda entry, *args: original_argv(
        "recovery_readout_v2.py" if entry == "recovery_readout.py" else entry, *args)
    try: return v1.execute(output)
    finally:
        s.verify = original_verify; v1._command_argv = original_argv; v1.b = original_b


def parse_args():
    ap = argparse.ArgumentParser(); ap.add_argument("command", choices=("run", "verify"));
    ap.add_argument("--output", type=Path, default=s.ATTEMPT); return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify": print(verify_v2()["identity"])
    else:
        result = execute(args.output); print({"complete": result["complete"], "error": result["error"]})
        raise SystemExit(0 if result["complete"] else 1)

