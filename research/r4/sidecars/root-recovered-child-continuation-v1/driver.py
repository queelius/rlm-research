"""Parent-only launch: inherited step3 -> original stages4..8 under a new3h envelope."""

import argparse
import fcntl
import json
import os
import shutil
import time
from pathlib import Path

import common as a
import native_amendment as amended
import campaign as coordinator
import campaign_native as native
import campaign_lifecycle_v2 as lifecycle

c = a.c
BASE_AUTHENTICATE_EXPORT = native.authenticate_export
BASE_OWNED_COMMAND = coordinator.owned_command


def schedule():
    result = [("training", 4), ("validation", 4)]
    for step in (5, 6, 7, 8):
        result.extend([("collection", step), ("training", step)])
        if step % 2 == 0:
            result.append(("validation", step))
    return result + [("selection", None), ("transfer", "original"), ("transfer", "selected")]


def selected_step(validations):
    return min(validations, key=lambda row: (-row["strict_successes"], row["step"]))["step"]


def run_envelope(started, gpu, amendment_id):
    return {"campaign_id": c.read(a.OLD / "CAMPAIGN.json")["campaign_id"],
        "campaign_sha256": c.file_hash(a.OLD / "CAMPAIGN.json"), "started_epoch": started,
        "deadline_epoch": started + a.CAP_SECONDS, "gpu": gpu,
        "continuation_amendment_id": amendment_id, "namespace": a.ROOT.name,
        "new_global_cap_seconds": a.CAP_SECONDS, "inherited_optimizer_steps": 3,
        "old_stop_preserved": True}


def committed_policies(run):
    policies = a.prior_policies()
    for directory in sorted(Path(run).glob("round-*")):
        generation_path = directory / "GENERATION.json"
        if not generation_path.exists():
            continue
        generation = c.read(generation_path)
        step = generation["round"]
        if not 4 <= step <= 8:
            raise ValueError("new output must not rewrite inherited generations0..3")
        checkpoint = directory / "training" / f"checkpoint-{step}/state.json"
        if not checkpoint.exists():
            continue
        if step - 1 not in policies:
            raise ValueError("continuation checkpoint chain is not contiguous")
        c.check_generation(generation, policies[step - 1], step - 1)
        binding = c.read(checkpoint)["input_identity"]["input_binding"]
        group_path = directory / "collection/export/GROUP.json"
        if (Path(binding["group_path"]).resolve() != group_path.resolve()
                or binding["group_sha256"] != c.file_hash(group_path)
                or binding["generation"] != generation
                or binding["continuation"]["amendment_id"] != a.verify_amendment()["amendment_id"]):
            raise ValueError("checkpoint not bound to exact amended group/generation")
        policy = c.checkpoint_policy(directory / "training", generation)
        commit = {"generation": generation, "policy": policy,
                  "checkpoint_state_sha256": policy["state_sha256"], "optimizer_steps": step}
        path = directory / "COMMIT.json"
        if path.exists() and c.read(path) != commit:
            raise ValueError("continuation commit changed")
        if not path.exists():
            c.write_once(path, commit)
        policies[step] = policy
    c.contiguous_steps([step for step in policies if step])
    return policies


def authenticate_export(output):
    manifest_path = Path(output) / "MANIFEST.json"
    manifest = c.read(manifest_path)
    if manifest.get("continuation_amendment_id"):
        return amended.authenticate_export(output)
    prior = c.read(a.ROOT / "PRIOR.json")
    if c.file_hash(manifest_path) not in {row["manifest_sha256"] for row in prior["validation_exports"].values()}:
        raise ValueError("unamended export is not one of the two fixed inherited validations")
    return BASE_AUTHENTICATE_EXPORT(output)


def dispatch_command(command):
    if not isinstance(command, list) or len(command) < 3:
        raise ValueError("unexpected continuation subprocess command")
    if command[:2] == [str(c.TRAIN_PYTHON), str(a.OLD / "campaign_train.py")]:
        return [command[0], str(a.ROOT / "train.py"), *command[2:]]
    if command[:3] == [str(c.NATIVE_PYTHON), str(a.OLD / "campaign_native.py"), "collect"]:
        return [command[0], str(a.ROOT / "native_amendment.py"), *command[2:]]
    raise ValueError("unexpected subprocess route; no new workflow authorized")


def owned_command(command, log_path, timeout, *, gpu=False):
    dispatched = dispatch_command(command)
    c.write_once(Path(log_path).with_suffix(".dispatch.json"),
        {"original_command": command, "actual_command": dispatched, "gpu": gpu,
         "amendment_id": a.verify_amendment()["amendment_id"], "timeout": timeout})
    return BASE_OWNED_COMMAND(dispatched, log_path, timeout, gpu=gpu)


def install():
    lifecycle.install()
    coordinator.committed_policies = committed_policies
    coordinator.owned_command = owned_command
    native.binding_for = amended.binding_for
    native.prepare_spec = amended.prepare_spec
    native.export = amended.export
    native.authenticate_export = authenticate_export


def stage_inherited(output):
    """Copy only small immutable exports. Checkpoints/raw traces remain referenced."""
    output = Path(output)
    prior = c.read(a.ROOT / "PRIOR.json")
    mapping = []
    sources = [(Path(row["path"]), output / f"validation-{int(step):02d}/export")
               for step, row in prior["validation_exports"].items()]
    sources.append((a.ROOT / "prepared-round04", output / "round-04/collection/export"))
    for source, destination in sources:
        destination.mkdir(parents=True, exist_ok=False)
        manifest = c.read(source / "MANIFEST.json")
        for name in [*manifest["artifact_sha256"], "MANIFEST.json"]:
            origin, target = source / name, destination / name
            if target.exists():
                raise ValueError("inherited target already exists")
            shutil.copyfile(origin, target)
            if c.file_hash(origin) != c.file_hash(target):
                raise ValueError("immutable inherited copy differs")
            mapping.append({"source": str(origin), "destination": str(target), "sha256": c.file_hash(target)})
    c.write_once(output / "round-04/GENERATION.json", c.read(a.OLD_RUN / "round-04/GENERATION.json"))
    c.write_once(output / "INHERITED_STAGES.json", {"prior_reference": str(a.ROOT / "PRIOR.json"),
        "prior_sha256": c.file_hash(a.ROOT / "PRIOR.json"), "copies": mapping,
        "policies": prior["policies"], "no_old_stage_mutations": True})


def verify_ready():
    amendment = a.verify_amendment()
    ready = c.read(a.ROOT / "READY.json")
    if ready["amendment_sha256"] != c.file_hash(a.ROOT / "AMENDMENT.json"):
        raise ValueError("READY amendment differs")
    c.authenticate(ready["artifact_sha256"])
    policies = a.prior_policies()
    proof = amended.authenticate_export(a.ROOT / "prepared-round04")
    return {"amendment_id": amendment["amendment_id"], "step3": policies[3], "prepared_export": proof, "gpu_calls": 0}


def run(args, started):
    verified = verify_ready()
    output = args.output.resolve()
    if args.command == "run":
        output.mkdir(parents=True, exist_ok=False)
        c.write_once(output / "RUN.json", run_envelope(started, os.environ["CUDA_VISIBLE_DEVICES"], verified["amendment_id"]))
        stage_inherited(output)
        c.write_once(output / "EXECUTION.json", {"amendment_sha256": c.file_hash(a.ROOT / "AMENDMENT.json"),
            "ready_sha256": c.file_hash(a.ROOT / "READY.json"), "run_sha256": c.file_hash(output / "RUN.json"),
            "entrypoint_sha256": c.file_hash(Path(__file__)), "schedule": schedule(),
            "original_coordinator_sha256": c.file_hash(Path(coordinator.__file__))})
    execution = c.read(output / "EXECUTION.json")
    c.authenticate({output / "RUN.json": execution["run_sha256"]})
    if (execution["amendment_sha256"] != c.file_hash(a.ROOT / "AMENDMENT.json")
            or execution["entrypoint_sha256"] != c.file_hash(Path(__file__))
            or c.read(output / "RUN.json")["continuation_amendment_id"] != verified["amendment_id"]):
        raise ValueError("resume execution/amendment identity changed")
    install()
    return coordinator.run_campaign(argparse.Namespace(output=output, resume=True))


if __name__ == "__main__":
    started = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run", "resume"))
    parser.add_argument("--output", type=Path, default=a.ROOT / "outputs/attempt-001")
    args = parser.parse_args()
    if args.command == "verify":
        result = verify_ready()
    else:
        gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
        if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
            raise ValueError("parent must assign one exclusively owned GPU and existing service credential")
        with (a.ROOT / "COORDINATOR.lock").open("a") as lease:
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = run(args, started)
    print(json.dumps(result, sort_keys=True, allow_nan=False))
