"""Additive exact-full-query external-file realization; science schedule unchanged."""

import hashlib
from pathlib import Path

import study as base


ROOT = base.ROOT
INPUTS = ROOT / "inputs-v3"
SPEC = ROOT / "SPEC_V3.json"
ATTEMPT = ROOT / "outputs/attempt-003"


def full_rows():
    source = base._csv_rows()
    result = []
    for selected in base.read(base.SELECTION)["rows"]:
        raw = source[selected["source_index"]]
        if base.digest(raw) != selected["row_sha256"]: raise ValueError("selected row changed")
        context, question = base.old_module().split_context_and_task(raw)
        if question != raw["view_ops"].strip(): raise ValueError("ordinary final question changed")
        result.append({"row_id": selected["row_sha256"], "queries": raw["queries"],
            "queries_sha256": hashlib.sha256(raw["queries"].encode()).hexdigest(),
            "context": context, "context_sha256": hashlib.sha256(context.encode()).hexdigest(),
            "question": question, "answer": raw["answer"]})
    if len({row["context_sha256"] for row in result}) != 1: raise ValueError("underlying context changed")
    return result


def environment_config(directory):
    return base.environment_config(directory)


def prepare_inputs(directory):
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    rows = full_rows(); by_id = {row["row_id"]: row for row in rows}; tasks = []
    for row in rows:
        path = directory / "full-queries" / (row["queries_sha256"] + ".txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists(): path.write_text(row["queries"]); path.chmod(0o444)
        if base.sha(path) != row["queries_sha256"]: raise ValueError("full queries file changed")
    for index, coordinate in enumerate(base.plan()):
        row = by_id[coordinate["row_id"]]
        tasks.append(base.old_module().MRCRData(idx=index, name=coordinate["id"],
            prompt=base.root_prompt(row["question"]), row_id=row["row_id"],
            document_sha256=row["queries_sha256"], arm="calibration").model_dump(mode="json", exclude_none=True))
    values = ((directory / "tasks.json", tasks),
        (directory / "PUBLIC.json", {"plan": base.plan(), "one_underlying_context": True,
            "full_query_sha256": {row["row_id"]: row["queries_sha256"] for row in rows}}),
        (directory / "HOST_GOLD.json", {row["row_id"]: row["answer"] for row in rows}))
    for path, value in values:
        if path.exists():
            if base.read(path) != value: raise ValueError("V3 immutable input differs")
        else: base.write_x(path, value)
    (directory / "HOST_GOLD.json").chmod(0o600)
    return {"tasks": 32, "full_query_files": 8, "underlying_contexts": 1,
        "environment": environment_config(directory), "query_map_sha256": base.digest(
            {row["row_id"]: row["queries_sha256"] for row in rows})}


def patch_task_setup(directory=INPUTS):
    directory = Path(directory); module = base.old_module()
    by_id = {row["row_id"]: row for row in full_rows()}
    async def setup(self, trace, runtime):
        del trace
        expected = by_id[self.data.row_id]["queries_sha256"]
        if self.data.document_sha256 != expected: raise ValueError("task/full-query binding changed")
        payload = (directory / "full-queries" / (expected + ".txt")).read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected: raise ValueError("full-query bytes changed")
        await runtime.write("/context.txt", payload)
        actual = await runtime.read("/context.txt")
        if hashlib.sha256(actual).hexdigest() != expected: raise ValueError("runtime full-query write changed")
    module.MRCRTask.setup = setup
    return module


def verify():
    base.verify_ready()
    ready = base.read(ROOT / "READY_V3.json")
    if ready["identity"] != base.digest({k: value for k, value in ready.items() if k != "identity"}):
        raise ValueError("READY_V3 identity changed")
    for path, expected in ready["closure_sha256"].items():
        if base.sha(path) != expected: raise ValueError("READY_V3 closure changed: " + path)
    return ready

