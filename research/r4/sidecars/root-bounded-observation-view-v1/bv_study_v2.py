"""Additive V2 binding with session-private raw-log harvest and no task raw file."""
import contextlib
import functools
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import uuid

import bv_study as v1

ROOT = Path(__file__).resolve().parent
ATTEMPT = ROOT / "outputs/attempt-002"
V1_READY_SHA = "a5a50377a481f1db75f81fd725c80ca4f6285a55bdf095b9ba3718ca5f788478"
if v1.sha(ROOT / "READY.json") != V1_READY_SHA:
    raise ValueError("bounded-view V1 seal changed")
v1_ready = v1.read(ROOT / "READY.json")
base, dose, NATIVE, OLD, JOINT = v1.base, v1.dose, v1.NATIVE, v1.OLD, v1.JOINT
sha, read, write, digest, load, aliases = v1.sha, v1.read, v1.write, v1.digest, v1.load, v1.aliases


def __getattr__(name):
    return getattr(v1, name)


def make_task(context, row, gold):
    original = base.make_task(context, {**row, "accumulation_arm": row["return_arm"]}, gold)
    original_setup, original_finalize = original.setup, original.finalize

    async def setup(trace, runtime):
        await original_setup(trace, runtime)
        await runtime.write(
            ".observation_view.json",
            json.dumps(
                {"schema": "bounded-observation-view-config-v1", "max_bytes": row["view_bytes"]},
                sort_keys=True,
            ).encode(),
        )

    async def finalize(trace, runtime):
        # The RLM harness deletes this session tree after task finalization. Harvest it now;
        # no raw ledger is written into the task cwd or shown in the policy message stream.
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
        if result.exit_code:
            trace.info["bounded_observation_view_v2"] = {
                "raw": None,
                "error": result.stderr,
                "policy_visibility": "session-tree harvest failed after rollout",
            }
        else:
            raw = result.stdout.strip()
            trace.info["bounded_observation_view_v2"] = {
                "raw": raw,
                "sha256": hashlib.sha256(raw.encode()).hexdigest(),
                "policy_visibility": "harvested after rollout from existing native session tree",
                "explicit_session_log_access_caveat": "system prompt advertises conversation log path; intervention changes passive next-request view, not filesystem access control",
            }
        await original_finalize(trace, runtime)

    original.setup, original.finalize = setup, finalize
    original.data = original.data.model_copy(
        update={"source_split": "accumulation-exposed-bounded-view-factorial-v2"}
    )
    return original


@functools.lru_cache(maxsize=1)
def stack():
    native = base.stack().native
    rows = {r["id"]: r for r in read(ROOT / "inputs/FREE_PLAN.json")}

    def task(context, prompt, gold, name):
        value = make_task(context, rows[name], gold)
        if value.data.prompt != prompt:
            raise ValueError("bounded-view V2 prompt changed")
        return value

    return SimpleNamespace(native=SimpleNamespace(**{**vars(native), "task": task}))


runtime, selected, protocol = base.runtime, base.selected, base.protocol


def binding():
    value = v1.binding()
    value["study"] = ROOT.name + "-v2"
    value["campaign_id"] = ROOT.name + "-v2"
    value["bounded_observation_view"]["ledger"] = "existing-session-tree-post-rollout-harvest"
    value["bounded_observation_view"]["attempt"] = "attempt-002"
    return value


def validate(value, descriptor, path):
    if value != binding():
        raise ValueError("bounded-view V2 binding changed")
    j = base.o.joint()
    validator = load(
        "bounded_view_v2_descriptor_validator",
        j.SOURCE / "binding.py",
        "865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1",
        {"study": j.original},
    )
    validator.validate_descriptor(value, descriptor, sha(path))


@functools.lru_cache(maxsize=1)
def interface(output):
    import bv_overlay_v2

    original = base.interface(output)
    values = {**vars(original)}
    original_installed = original.installed

    @contextlib.contextmanager
    def installed(binding, target, plan, public):
        from verifiers.v1.harnesses.rlm.harness import RLMHarness

        with original_installed(binding, target, plan, public):
            prior = RLMHarness.setup

            async def setup(self, runtime):
                await prior(self, runtime)
                result = await runtime.run(["python", "-c", bv_overlay_v2.overlay_program()], {})
                write(
                    output / "bounded-view-v2-overlays" / (uuid.uuid4().hex + ".json"),
                    {
                        "runtime": runtime.name,
                        "program_sha256": digest(bv_overlay_v2.overlay_program()),
                        "exit_code": result.exit_code,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    },
                )
                if result.exit_code:
                    raise RuntimeError("bounded observation V2 overlay failed")

            RLMHarness.setup = setup
            try:
                yield
            finally:
                RLMHarness.setup = prior

    values["installed"] = installed
    return SimpleNamespace(**values)


def verify():
    ready = read(ROOT / "READY_v2.json")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("bounded-view V2 identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        dose.check(path, pin)
    return ready
