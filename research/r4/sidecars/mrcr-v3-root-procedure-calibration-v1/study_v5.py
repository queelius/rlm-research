"""V5 task-setup dispatch repair; V4 runtime and V3 science stay exact."""

import hashlib
from pathlib import Path

import study as base
import study_v4 as v4


ROOT = base.ROOT
INPUTS = v4.INPUTS
SPEC = v4.SPEC
ATTEMPT = ROOT / "outputs/attempt-005"
RUNTIME = v4.RUNTIME
RUNTIME_BIN = v4.RUNTIME_BIN
IMAGE = v4.IMAGE
plan = base.plan
full_rows = v4.full_rows
environment_config = v4.environment_config
verify_allocation_runtime = v4.verify_allocation_runtime


def patch_environment(env, directory=INPUTS):
    """Patch the canonical registry-loaded task class, not the unused alias class."""
    directory = Path(directory)
    by_id = {row["row_id"]: row for row in full_rows()}

    async def setup(self, trace, runtime):
        del trace
        expected = by_id[self.data.row_id]["queries_sha256"]
        if self.data.document_sha256 != expected:
            raise ValueError("task/full-query binding changed")
        path = directory / "full-queries" / (expected + ".txt")
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError("frozen full-query bytes changed")
        await runtime.write("/context.txt", payload)
        actual = await runtime.read("/context.txt")
        if hashlib.sha256(actual).hexdigest() != expected:
            raise ValueError("actual task setup full-query write/read changed")

    classes = {type(task) for task in env.taskset}
    if len(classes) != 1:
        raise ValueError("expected one canonical MRCR task class")
    task_class = classes.pop()
    if task_class.__module__ != "mrcr_rootless_document_baseline_v2":
        raise ValueError("MRCR task registry resolved unexpected implementation")
    task_class.setup = setup
    return env


def verify():
    v4.verify()
    ready = base.read(ROOT / "READY_V5.json")
    if ready["identity"] != base.digest({k: value for k, value in ready.items() if k != "identity"}):
        raise ValueError("READY_V5 identity changed")
    for path, expected in ready["closure_sha256"].items():
        if base.sha(path) != expected:
            raise ValueError("READY_V5 closure changed: " + path)
    verify_allocation_runtime()
    return ready

