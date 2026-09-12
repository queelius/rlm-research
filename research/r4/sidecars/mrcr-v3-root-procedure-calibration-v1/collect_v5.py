"""V5 collector binds setup to the registry-loaded task class."""

import argparse
import asyncio
from pathlib import Path

import collect_v4 as v4
import study_v5


def environment(directory):
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    env = SingleAgentEnv(
        SingleAgentEnvConfig.model_validate(study_v5.environment_config(directory))
    )
    return study_v5.patch_environment(env, directory)


async def run(spec_path, endpoint_path, output, deadline):
    original = v4.environment
    v4.environment = environment
    try:
        return await v4.run(spec_path, endpoint_path, output, deadline)
    finally:
        v4.environment = original


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.spec, args.endpoint, args.output, args.deadline)))

