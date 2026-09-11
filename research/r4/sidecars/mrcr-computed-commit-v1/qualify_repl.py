"""Owned CPU-only real-REPL test launcher; never requests an inference endpoint."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
DOCKER = ROOT.parent / 'rootless-runtime-feasibility-v1/bin'
IMAGE = 'localhost/verifiers-rlm-python:3.11-slim-single-id-v1'


async def run(output, overlay):
    from verifiers.v1.harnesses.rlm.harness import RLMHarness, RLMHarnessConfig
    from verifiers.v1.runtimes.docker import DockerRuntime, DockerConfig
    output.mkdir(parents=True, exist_ok=False)
    os.environ['PATH'] = str(DOCKER) + os.pathsep + os.environ.get('PATH', '')
    runtime = DockerRuntime(DockerConfig(image=IMAGE, workdir='/app'), name='mrcr-submit-repl-' + uuid4().hex)
    harness = RLMHarness(RLMHarnessConfig(version='4ef3438', max_depth=0))
    try:
        await runtime.start()
        await asyncio.wait_for(harness.setup(runtime), 180)
        result = await runtime.run(['sh', '-c', 'find /root/.local/share/uv/tools -mindepth 3 -maxdepth 3 -path "*/bin/python" -type l'], {})
        candidates = result.stdout.splitlines()
        if result.exit_code or len(candidates) != 1:
            raise RuntimeError('cannot identify unique owned nano Python: ' + repr(candidates))
        python = candidates[0]
        if overlay:
            from overlay import install_in_runtime
            await install_in_runtime(runtime, byte_cap=64)
        await runtime.write('/app/test_repl.py', (ROOT / 'test_repl_in_container.py').read_bytes())
        # Engine import installs the additive overlay before the real REPL test.
        code = "import rlm.engine,runpy;runpy.run_path('/app/test_repl.py',run_name='__main__')"
        result = await runtime.run([python, '-c', code], {})
        record = {'overlay': overlay, 'exit_code': result.exit_code, 'stdout': result.stdout,
                  'stderr': result.stderr, 'runtime': runtime.name, 'gpu_calls': 0}
        (output / 'RESULT.json').write_text(json.dumps(record, indent=2) + '\n')
        print(json.dumps(record), flush=True)
        return result.exit_code
    finally:
        await runtime.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--overlay', action='store_true')
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.output, args.overlay)))
