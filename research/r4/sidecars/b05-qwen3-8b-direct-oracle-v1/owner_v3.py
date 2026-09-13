"""Attempt-003 owner with the exact engine-entry lifecycle claim installed."""

import argparse
import json
import sys
import types

import collect_v3 as collect
import study_v3 as study


OWNER_SOURCE_SHA256 = "40463e9850e3879c15fbeb544320fbf2d19dfd459bb368b3ab81812058295859"
OLD = (
    "suite=base.study.dependencies();suite.SERVE=study.SERVICE;"
    "suite.life.__dict__['ALLOCATION_SERVICE']=study.SERVICE;suite.preflight=preflight"
)
NEW = (
    "suite=base.study.dependencies();lifecycle.install(suite);suite.SERVE=study.SERVICE;"
    "suite.life.__dict__['ALLOCATION_SERVICE']=study.SERVICE;suite.preflight=preflight"
)


def lifecycle_module():
    musique_study = study.load("b05_qwen8_musique_study_v3", study.MUSIQUE / "study_v3.py")
    old = sys.modules.get("study_v3")
    sys.modules["study_v3"] = musique_study
    try:
        return study.load("b05_qwen8_musique_lifecycle_v3", study.MUSIQUE / "lifecycle_v3.py")
    finally:
        if old is None:
            sys.modules.pop("study_v3", None)
        else:
            sys.modules["study_v3"] = old


lifecycle = lifecycle_module()


def configure_suite(suite):
    lifecycle.install(suite)
    suite.SERVE = study.SERVICE
    suite.life.ALLOCATION_SERVICE = study.SERVICE
    return suite


def implementation():
    path = study.ROOT / "owner.py"
    if study.sha(path) != OWNER_SOURCE_SHA256:
        raise ValueError("sealed owner source changed")
    text = path.read_text()
    if text.count(OLD) != 1:
        raise ValueError("owner lifecycle seam changed")
    text = text.replace(OLD, NEW)
    old_study, old_collect = sys.modules.get("study"), sys.modules.get("collect")
    sys.modules["study"], sys.modules["collect"] = study, collect
    try:
        module = types.ModuleType("b05_qwen8_owner_lifecycle_repaired")
        module.__file__ = str(path) + ":lifecycle-v3"
        module.lifecycle = lifecycle
        exec(compile(text, module.__file__, "exec"), module.__dict__)
    finally:
        if old_study is None:
            sys.modules.pop("study", None)
        else:
            sys.modules["study"] = old_study
        if old_collect is None:
            sys.modules.pop("collect", None)
        else:
            sys.modules["collect"] = old_collect
    module.study, module.collect, module.lifecycle = study, collect, lifecycle
    return module


source = implementation()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["verify", "run"])
    parser.add_argument("--outer-seconds", type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        result = source.execute(args.outer_seconds)
        print(json.dumps(result))
        raise SystemExit(0 if result["complete"] else 1)

