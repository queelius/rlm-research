"""Qualified native task/render interface in the terminal-RLVR namespace."""
import json
import terminal_study as study

SOURCE = study.QSR / "qsr_native.py"
PIN = "02aea033ef02a215577af03e18769adda0d9994e947900b310b1a7ee8356441c"
with study.aliases({"qsr_study": study}):
    qualified = study.load("terminal_qualified_qsr_native", SOURCE, PIN)

stack = qualified.stack
prompt = qualified.prompt
make_task = qualified.make_task
first_prefix = qualified.first_prefix
interface = qualified.interface
exact_turns = qualified.exact_turns
validate_typed_audit = qualified.validate_typed_audit


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify-export",))
    parser.add_argument("--output", type=__import__("pathlib").Path, required=True)
    args = parser.parse_args()
    from terminal_export import authenticate_export
    print(json.dumps(authenticate_export(args.output), sort_keys=True))
