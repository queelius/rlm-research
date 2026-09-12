"""Final owner: sealed V1 logic with the fresh child process pointed at collect_v2.py."""

import argparse
import ast
import json
from pathlib import Path
import signal
import time
import types

import collect_v3
import owner as original
import study
import study_v3


def physical_request_count(output):
    output = Path(output)
    typed = {path.relative_to(output / "blocks") for path in
             output.glob("blocks/*/collection/rollout/typed-audit/*-request.json")}
    roles = {Path(*path.relative_to(output / "blocks").parts[:-2], "typed-audit",
                  path.name) for path in
             output.glob("blocks/*/collection/rollout/role-audit/*-request.json")}
    if typed != roles:
        raise ValueError("typed/role physical request audit inventories differ")
    status_total = 0
    for path in output.glob("blocks/*/collection/rollout/STATUS.json"):
        status_total += json.loads(path.read_text())["physical_attempts"]
    if status_total and status_total != len(typed):
        raise ValueError("STATUS physical_attempts differs from physical request audits")
    return len(typed)


def physical_request_audit(output):
    count = physical_request_count(output)
    return {"physical_requests": count, "typed_request_files": count,
            "role_request_files": count, "status_physical_attempts": count,
            "historical_reference_parity": {"typed": 230, "role": 230,
                                             "status_physical_attempts": 230}}


def cleanup_alarm_seconds(owned_deadline, now=None):
    remaining = owned_deadline - (time.time() if now is None else now)
    return min(90.0, remaining) if remaining > 0 else None


def _arm_cleanup(owned_deadline, errors):
    seconds = cleanup_alarm_seconds(owned_deadline)
    if seconds is None:
        # The ownership deadline has already fired. Avoid a second .001-second signal that
        # prevents release; mark the run failed and leave the 1900-second external kill bound.
        errors.append({"stage": "ownership-deadline", "message":
                       "1800-second owned deadline expired before clean release"})
        signal.setitimer(signal.ITIMER_REAL, 0)
    else:
        signal.setitimer(signal.ITIMER_REAL, seconds)


def _implementation():
    source = Path(original.__file__).read_text()
    replacements = {
        'str(study.ROOT / "collect.py")': 'str(study.ROOT / "collect_v3.py")',
        "work = owned - 120": "work = owned - 180",
        "result = score.compute(exported_rows)":
            "request_audit = physical_request_audit(output)\n        result = score.compute(exported_rows)\n        result['physical_request_audit'] = request_audit",
        "signal.setitimer(signal.ITIMER_REAL, max(0.001, min(owned, time.time() + 90) - time.time()))":
            "_arm_cleanup(owned, errors)",
    }
    if any(source.count(before) != 1 for before in replacements):
        raise ValueError("sealed owner collector-path seam changed")
    for before, after in replacements.items():
        source = source.replace(before, after)
    tree = ast.parse(source)
    node = next(item for item in tree.body
                if isinstance(item, ast.FunctionDef) and item.name == "execute")
    module = types.ModuleType("recursion_headroom_owner_v3_implementation")
    module.__dict__.update(original.__dict__)
    module.collect = collect_v3
    module.study.verify = study_v3.verify
    module.physical_request_audit = physical_request_audit
    module._arm_cleanup = _arm_cleanup
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(original.__file__) + ":v3", "exec"),
         module.__dict__)
    return module


execute = _implementation().execute


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=study.ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=study.OUTER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(study_v3.verify()["identity"])
    else:
        result = execute(args.output, args.outer_seconds)
        print(result)
        raise SystemExit(0 if result["complete"] else 1)
