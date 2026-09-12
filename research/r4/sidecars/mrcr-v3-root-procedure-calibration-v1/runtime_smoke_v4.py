"""Real CPU sandbox smoke for the allocation image used by V4."""

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import time

import study_v4


async def smoke(output):
    from verifiers.v1.runtimes.docker import DockerConfig, DockerRuntime

    output = Path(output)
    if output.exists():
        raise ValueError("write-once smoke receipt required")
    study_v4.verify_allocation_runtime()
    row = study_v4.full_rows()[0]
    payload = row["queries"].encode()
    expected = row["queries_sha256"]
    before = os.environ.get("PATH", "")
    os.environ["PATH"] = str(study_v4.RUNTIME_BIN) + os.pathsep + before
    runtime = DockerRuntime(
        DockerConfig(**study_v4.environment_config(study_v4.INPUTS)["agent"]["runtime"], allow=["*"]),
        name=f"mrcr-v4-cpu-smoke-{os.getpid()}-{int(time.time())}",
    )
    started = time.time()
    stopped = False
    try:
        await runtime.start()
        await runtime.write("/context.txt", payload)
        actual = await runtime.read("/context.txt")
        process = await runtime.run(
            ["python3", "-c", "import hashlib; print(hashlib.sha256(open('/context.txt','rb').read()).hexdigest())"],
            {},
        )
        if hashlib.sha256(actual).hexdigest() != expected:
            raise ValueError("runtime API readback changed frozen full-query bytes")
        if process.exit_code != 0 or process.stdout.strip() != expected:
            raise ValueError("in-container Python readback changed frozen full-query bytes")
    finally:
        await runtime.stop()
        stopped = True
        os.environ["PATH"] = before
    receipt = {
        "schema": "mrcr-v4-allocation-runtime-smoke-v1",
        "image": study_v4.IMAGE,
        "wrapper": str(study_v4.RUNTIME_BIN / "docker"),
        "source_queries_sha256": expected,
        "bytes": len(payload),
        "runtime_api_read_sha256": hashlib.sha256(actual).hexdigest(),
        "in_container_python_read_sha256": process.stdout.strip(),
        "container_stopped": stopped,
        "elapsed_seconds": time.time() - started,
        "gpu_calls": 0,
    }
    study_v4.base.write_x(output, receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(smoke(args.output)), sort_keys=True))
