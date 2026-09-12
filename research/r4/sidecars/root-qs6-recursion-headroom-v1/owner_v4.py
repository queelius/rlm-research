"""Attempt-002 owner with the recovery dependency import chain isolated end to end."""

import argparse
import functools
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace

import collect_v3
import owner_v3
import study
import study_v4


_RECOVERY_IMPORT_NAMES = (
    "owner_v7", "study_v7", "study_v6", "study_v5", "study_v4", "study_v3",
    "study_v2", "study", "protocol",
)


@functools.lru_cache(maxsize=1)
def dependencies():
    """Load every generic recovery ancestor from RECOVERY, then restore local aliases."""
    saved_modules = {name: sys.modules.get(name) for name in _RECOVERY_IMPORT_NAMES}
    saved_path = list(sys.path)
    try:
        for name in _RECOVERY_IMPORT_NAMES: sys.modules.pop(name, None)
        sys.path.insert(0, str(study.RECOVERY)); importlib.invalidate_caches()
        recovery_owner = importlib.import_module("owner_v7")
        if Path(recovery_owner.__file__).resolve() != (study.RECOVERY / "owner_v7.py").resolve():
            raise ValueError("recovery owner resolved outside frozen recovery sidecar")
        # owner_v7's live chain is v7 -> v4 -> v3 -> v2 -> study. V5/V6 are
        # historical siblings, deliberately evicted but not expected to load.
        expected = {f"study_v{version}": study.RECOVERY / f"study_v{version}.py"
            for version in (2, 3, 4, 7)}
        expected["study"] = study.RECOVERY / "study.py"
        for name, path in expected.items():
            module = sys.modules.get(name)
            if module is None or Path(module.__file__).resolve() != path.resolve():
                raise ValueError("recovery ancestor resolved outside isolated chain: " + name)
        recovery_owner.s.bind_runtime(recovery_owner.qualified)
        suite = recovery_owner.qualified.dependencies()
        if not all(callable(getattr(suite, name, None)) for name in ("start_service", "release_service", "command")):
            raise ValueError("qualified dependency suite interface differs")
        return suite
    finally:
        sys.path[:] = saved_path
        for name, module in saved_modules.items():
            if module is None: sys.modules.pop(name, None)
            else: sys.modules[name] = module


facade = SimpleNamespace(**vars(study))
facade.ATTEMPT = study_v4.ATTEMPT
facade.verify = study_v4.verify
implementation = owner_v3._implementation()
implementation.study = facade
implementation.collect = collect_v3
implementation.dependencies = dependencies
execute = implementation.execute


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=study_v4.ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=study.OUTER_SECONDS); args = parser.parse_args()
    if args.command == "verify": print(study_v4.verify()["identity"])
    else:
        result = execute(args.output, args.outer_seconds); print(result)
        raise SystemExit(0 if result["complete"] else 1)
