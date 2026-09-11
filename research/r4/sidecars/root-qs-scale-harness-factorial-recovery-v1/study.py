"""Attempt-002 namespace with the complete qualified collector study interface."""

import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT.parent / "root-qs-scale-harness-factorial-v1"
spec = importlib.util.spec_from_file_location("scale_harness_recovery_original_study", ORIGINAL / "study.py")
prior = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = prior
spec.loader.exec_module(prior)

SIDE, QS_REPLICATION, QS, RECOVERY, AE, BV = (
    prior.SIDE,
    prior.QS_REPLICATION,
    prior.QS,
    prior.RECOVERY,
    prior.AE,
    prior.BV,
)
ATTEMPT = ROOT / "outputs/attempt-002"
NATIVE = prior.NATIVE
CHILD_SHA = prior.CHILD_SHA
base = prior.base
JOINT = base.JOINT
LABELS = base.base.problem.LABELS
corpus = base.corpus
answer = base.answer
load = base.load
read, write, sha, digest, aliases = prior.read, prior.write, prior.sha, prior.digest, prior.aliases
runtime, interface, binding, validate = (
    prior.runtime,
    prior.interface,
    prior.binding,
    prior.validate,
)


def make_task(context, row, gold):
    task = base.base.qnative().make_task(context, row["question"], gold, row["id"])
    original_setup, original_finalize = task.setup, task.finalize

    async def setup(trace, runtime):
        await original_setup(trace, runtime)
        await runtime.write("batch_contract.py", prior.task_protocol.helper_bytes(row["return_arm"]))
        await runtime.write(
            ".observation_view.json",
            json.dumps(
                {"schema": "bounded-observation-view-config-v1", "max_bytes": row["view_bytes"]},
                sort_keys=True,
            ).encode(),
        )

    async def finalize(trace, runtime):
        script = (
            "import json,pathlib,sys\n"
            "root=pathlib.Path('.vf-rlm')/sys.argv[1]/'home'/'sessions'\n"
            "rows=[]\n"
            "for path in sorted(root.rglob('messages.jsonl')):\n"
            "  for line in path.read_text().splitlines():\n"
            "    row=json.loads(line)\n"
            "    if row.get('type') in ('tool_result','bounded_observation_view'):\n"
            "      row['session_log']=str(path);rows.append(row)\n"
            "print(json.dumps(rows,sort_keys=True))"
        )
        result = await runtime.run(["python", "-c", script, trace.id], {})
        raw = result.stdout.strip() if result.exit_code == 0 else None
        trace.info["scale_harness_observations"] = {
            "raw": raw,
            "sha256": hashlib.sha256(raw.encode()).hexdigest() if raw is not None else None,
            "error": result.stderr if result.exit_code else None,
            "policy_visibility": "post-rollout session-tree harvest",
            "filesystem_access_caveat": (
                "The intervention changes the passive next-request view, not filesystem access control."
            ),
        }
        await original_finalize(trace, runtime)

    task.setup, task.finalize = setup, finalize
    task.data = task.data.model_copy(
        update={
            "prompt": task.data.prompt + prior.task_protocol.extra_prompt(row["return_arm"]),
            "source_split": "root-training-manifest-new_child-c32-training-exposed",
        }
    )
    return task


@functools.lru_cache(maxsize=1)
def stack():
    native = base.base.qnative().stack().native
    rows = {row["id"]: row for row in read(ROOT / "inputs/FREE_PLAN.json")}

    def task(context, prompt, gold, name):
        value = make_task(context, rows[name], gold)
        if value.data.prompt != prompt:
            raise ValueError("frozen recovery scale-harness prompt changed")
        return value

    return SimpleNamespace(native=SimpleNamespace(**{**vars(native), "task": task}))


def protocol():
    import protocol as local_protocol

    return local_protocol


def verify():
    prior.verify()
    ready = read(ROOT / "READY_v2.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("recovery READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError("recovery closure changed: " + path)
    return ready
