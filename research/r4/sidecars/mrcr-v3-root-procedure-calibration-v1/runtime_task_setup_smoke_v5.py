"""Invoke the actual registry-loaded frozen task setup in the real allocation runtime."""

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import time

import collect_v5
import study as base
import study_v5


async def smoke(output):
    from verifiers.v1.runtimes.docker import DockerConfig, DockerRuntime

    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    study_v5.verify_allocation_runtime()
    env = collect_v5.environment(study_v5.INPUTS)
    task = list(env.taskset)[0]
    expected = task.data.document_sha256
    before = os.environ.get("PATH", "")
    os.environ["PATH"] = str(study_v5.RUNTIME_BIN) + os.pathsep + before
    runtime = DockerRuntime(
        DockerConfig(**study_v5.environment_config(study_v5.INPUTS)["agent"]["runtime"], allow=["*"]),
        name=f"mrcr-v5-task-setup-smoke-{os.getpid()}-{int(time.time())}",
    )
    started = time.time()
    stopped = False
    try:
        await runtime.start()
        await task.setup(None, runtime)
        actual = await runtime.read("/context.txt")
        process = await runtime.run(
            ["python3", "-c", "import hashlib; print(hashlib.sha256(open('/context.txt','rb').read()).hexdigest())"],
            {},
        )
        if hashlib.sha256(actual).hexdigest() != expected:
            raise ValueError("post-setup runtime read differs")
        if process.exit_code or process.stdout.strip() != expected:
            raise ValueError("post-setup in-container read differs")
    finally:
        await runtime.stop()
        stopped = True
        os.environ["PATH"] = before
    receipt = {
        "schema": "mrcr-v5-actual-task-setup-smoke-v1",
        "task_class_module": type(task).__module__,
        "task_name": task.data.name,
        "task_document_sha256": expected,
        "runtime_read_sha256": hashlib.sha256(actual).hexdigest(),
        "in_container_read_sha256": process.stdout.strip(),
        "runtime_image": study_v5.IMAGE,
        "runtime_wrapper": str(study_v5.RUNTIME_BIN / "docker"),
        "container_stopped": stopped,
        "elapsed_seconds": time.time() - started,
        "model_calls": 0,
        "gpu_calls": 0,
    }
    base.write_x(output, receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(smoke(args.output)), sort_keys=True))
