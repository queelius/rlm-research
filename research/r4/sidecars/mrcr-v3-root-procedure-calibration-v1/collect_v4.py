"""V4 collector: exact V3 science with the allocation-qualified local runtime."""

import argparse
import asyncio
from collections.abc import MutableMapping
import os
from pathlib import Path
from types import SimpleNamespace

import collect as base_collect
import study as base_study
import study_v4


class _EnvironmentProxy(MutableMapping):
    def __init__(self, value):
        self.value = value

    def __getitem__(self, key):
        return self.value[key]

    def __delitem__(self, key):
        del self.value[key]

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __setitem__(self, key, value):
        failed_prefix = str(base_study.ROOT / "bin") + os.pathsep
        if key == "PATH" and value.startswith(failed_prefix):
            value = str(study_v4.RUNTIME_BIN) + os.pathsep + value[len(failed_prefix):]
        self.value[key] = value

    def get(self, key, default=None):
        return self.value.get(key, default)

    def setdefault(self, key, default=None):
        return self.value.setdefault(key, default)


def environment(directory):
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    study_v4.patch_task_setup(directory)
    return SingleAgentEnv(
        SingleAgentEnvConfig.model_validate(study_v4.environment_config(directory))
    )


def _redirect(path):
    path = Path(path)
    mapping = {
        base_study.ROOT / "SPEC.json": study_v4.SPEC,
        base_study.ROOT / "inputs/HOST_GOLD.json": study_v4.INPUTS / "HOST_GOLD.json",
    }
    return mapping.get(path, path)


async def run(spec_path, endpoint_path, output, deadline):
    original_read, original_sha = base_study.read, base_study.sha
    original_environment, original_os = base_collect.environment, base_collect.os
    base_study.read = lambda path: original_read(_redirect(path))
    base_study.sha = lambda path: original_sha(_redirect(path))
    base_collect.environment = lambda _directory: environment(study_v4.INPUTS)
    base_collect.os = SimpleNamespace(environ=_EnvironmentProxy(os.environ), pathsep=os.pathsep)
    study_v4.patch_task_setup(study_v4.INPUTS)
    try:
        return await base_collect.run(spec_path, endpoint_path, output, deadline)
    finally:
        base_study.read, base_study.sha = original_read, original_sha
        base_collect.environment, base_collect.os = original_environment, original_os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.spec, args.endpoint, args.output, args.deadline)))

