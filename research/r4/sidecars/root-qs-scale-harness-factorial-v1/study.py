"""Question-sensitive root pair with the qualified return/view harness bundle."""

from __future__ import annotations

import contextlib
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import uuid


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
ATTEMPT = ROOT / "outputs/attempt-001"
QS_REPLICATION = SIDE / "root-question-sensitive-seed-replication-v1"
QS = SIDE / "root-question-sensitive-sft-v1"
RECOVERY = SIDE / "root-question-sensitive-sft-recovery-v1"
AE = SIDE / "root-acquired-evidence-accumulation-v1"
BV = SIDE / "root-bounded-observation-view-v1"
for directory in (QS_REPLICATION, QS, RECOVERY, AE, BV):
    sys.path.insert(0, str(directory))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = _load("scale_harness_qs_replication", QS_REPLICATION / "study.py")
task_protocol = _load("scale_harness_accumulation_protocol", AE / "ae_protocol.py")
import bv_overlay_v2 as view_overlay

read, write, sha, digest, aliases = base.read, base.write, base.sha, base.digest, base.aliases
NATIVE = base.NATIVE
CHILD_SHA = base.base.CHILD_SHA


def runtime():
    return base.runtime()


def protocol():
    import qs_protocol

    return qs_protocol


def binding(arm):
    value = base.binding(arm)
    value["study"] = ROOT.name
    value["campaign_id"] = ROOT.name
    value["scale_harness_factorial"] = {
        "schema": "root-qs-scale-harness-factorial-binding-v1",
        "endpoints": 64,
        "root_policies": ["unchanged", "sft6"],
        "return_arms": ["B", "C"],
        "visible_view_max_bytes": [4096, 20000],
        "visible_view_unit": "bytes",
        "package_is_not_isolated_memory_effect": True,
        "fixed_child": "c32",
        "no_training": True,
    }
    if value["models"][value["fixed_child"]]["adapter_sha256"] != CHILD_SHA:
        raise ValueError("fixed c32 child changed")
    return value


def validate(value, descriptor, path):
    arm = value.get("question_sensitive", {}).get("arm")
    if value != binding(arm):
        raise ValueError("scale-harness binding changed")
    joint = base.base.joint()
    validator = base.load(
        "scale_harness_descriptor_validator",
        joint.SOURCE / "binding.py",
        "865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1",
        {"study": joint.original},
    )
    validator.validate_descriptor(value, descriptor, sha(path))


def make_task(context, row, gold):
    task = base.base.qnative().make_task(context, row["question"], gold, row["id"])
    original_setup, original_finalize = task.setup, task.finalize

    async def setup(trace, runtime_value):
        await original_setup(trace, runtime_value)
        await runtime_value.write("batch_contract.py", task_protocol.helper_bytes(row["return_arm"]))
        await runtime_value.write(
            ".observation_view.json",
            json.dumps(
                {"schema": "bounded-observation-view-config-v1", "max_bytes": row["view_bytes"]},
                sort_keys=True,
            ).encode(),
        )

    async def finalize(trace, runtime_value):
        # Post-rollout harvest of the existing session log; never added to policy history.
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
        result = await runtime_value.run(["python", "-c", script, trace.id], {})
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
        await original_finalize(trace, runtime_value)

    task.setup, task.finalize = setup, finalize
    task.data = task.data.model_copy(
        update={
            "prompt": task.data.prompt + task_protocol.extra_prompt(row["return_arm"]),
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
            raise ValueError("frozen scale-harness prompt changed")
        return value

    return SimpleNamespace(native=SimpleNamespace(**{**vars(native), "task": task}))


@functools.lru_cache(maxsize=1)
def interface(output):
    original = base.base.interface(output)
    values = {**vars(original)}
    original_installed = original.installed

    @contextlib.contextmanager
    def installed(actual_binding, target, plan, public):
        from verifiers.v1.harnesses.rlm.harness import RLMHarness

        with original_installed(actual_binding, target, plan, public):
            prior = RLMHarness.setup

            async def setup(self, runtime_value):
                await prior(self, runtime_value)
                program = view_overlay.overlay_program()
                result = await runtime_value.run(["python", "-c", program], {})
                write(
                    Path(output) / "bounded-view-overlays" / (uuid.uuid4().hex + ".json"),
                    {
                        "runtime": runtime_value.name,
                        "program_sha256": digest(program),
                        "exit_code": result.exit_code,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    },
                )
                if result.exit_code:
                    raise RuntimeError("qualified bounded-view overlay failed")

            RLMHarness.setup = setup
            try:
                yield
            finally:
                RLMHarness.setup = prior

    values["installed"] = installed
    return SimpleNamespace(**values)


def verify():
    base.verify()
    ready = read(ROOT / "READY_v3.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity changed")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError("frozen source/input changed: " + path)
    for arm in ("unchanged", "sft6"):
        binding(arm)
    return ready
