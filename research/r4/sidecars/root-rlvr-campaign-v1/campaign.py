"""Parent-invoked serial service→fresh capture→one update campaign. No implicit retries."""

import argparse
import fcntl
import json
import os
import signal
import socket
import subprocess
import time
import traceback
import uuid
from pathlib import Path

import campaign_common as c
import campaign_native as native


def remaining(deadline):
    value = deadline - time.time()
    if value <= 0:
        raise TimeoutError("campaign four-hour global envelope exhausted")
    return value


def process_identity(pid):
    path = Path(f"/proc/{pid}")
    if not path.exists():
        return None
    stat = (path / "stat").read_text().split(")", 1)[1].split()
    if stat[0] == "Z":
        return None
    return {"pid": pid, "uid": path.stat().st_uid, "pgid": os.getpgid(pid),
            "start_ticks": int(stat[19]), "argv": (path / "cmdline").read_bytes().decode().rstrip("\x00").split("\x00")}


def ports_free():
    for port in (18601, 18611, 18621):
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return False
    return True


def claim_service(service):
    owner_path = service.parent / "SERVICE_OWNER.json"
    if owner_path.exists():
        return c.read(owner_path)
    if not (service / "SERVER_START.json").exists():
        return None
    start = c.read(service / "SERVER_START.json")
    for path in (service / "inference.json", service / "inference.log"):
        if path.exists():
            path.chmod(0o600)  # The inherited service config/log can contain its API key.
    identity = process_identity(start["pid"])
    if identity is None:
        return None
    command = start["command"]
    if (identity["uid"] != os.getuid() or identity["pgid"] != identity["pid"]
            or command[-2:] != ["@", str(service / "inference.json")]
            or identity["argv"][-len(command):] != command
            and identity["argv"][-2:] != command[-2:]):
        raise ValueError("cannot authenticate owned inference process")
    owner = {"process": identity, "server_start_sha256": c.file_hash(service / "SERVER_START.json"),
             "binding_sha256": c.file_hash(service / "BINDING.json"), "service": str(service),
             "gpu": start["gpu"]}
    c.write_once(owner_path, owner)
    return owner


def stop_service(service):
    """Signal only the exact process group previously authenticated for this directory."""
    stopped = service.parent / "SERVICE_STOPPED.json"
    if stopped.exists():
        if not ports_free():
            raise ValueError("ports occupied after previous owned-service stop; no broad cleanup")
        return
    owner = claim_service(service)
    if owner:
        c.authenticate({service / "SERVER_START.json": owner["server_start_sha256"],
                        service / "BINDING.json": owner["binding_sha256"]})
        expected = owner["process"]
        actual = process_identity(expected["pid"])
        if actual is not None and actual != expected:
            raise ValueError("PID/group identity changed; refusing to signal")
        for sig, seconds in ((signal.SIGINT, 30), (signal.SIGTERM, 20), (signal.SIGKILL, 10)):
            if process_identity(expected["pid"]) is None:
                break
            if process_identity(expected["pid"]) != expected:
                raise ValueError("owned PID identity changed during stop")
            os.killpg(expected["pgid"], sig)
            until = time.monotonic() + seconds
            while time.monotonic() < until and process_identity(expected["pid"]) is not None:
                time.sleep(.2)
        if process_identity(expected["pid"]) is not None:
            raise RuntimeError("owned service did not stop")
    if not ports_free():
        raise RuntimeError("inference ports remain occupied; do not overlap training or kill unrelated processes")
    c.write_once(stopped, {"stopped_at": time.time(), "owner": owner, "ports_free": True})


def start_service(directory, policy, deadline):
    directory.mkdir(parents=True, exist_ok=False)
    binding = native.binding_for(policy)
    binding_path = directory / "BINDING.json"
    c.write_once(binding_path, binding)
    service = directory / "service"
    if not ports_free():
        raise ValueError("service ports are already occupied; parent must free the sole device")
    command = [str(c.NATIVE_PYTHON), str(c.ROLE / "source/serve.py"), "--binding", str(binding_path), "--run-dir", str(service)]
    c.write_once(directory / "SERVICE_REQUEST.json", {"command": command, "policy": policy,
        "campaign_sha256": c.file_hash(c.ROOT / "CAMPAIGN.json"), "gpu": os.environ["CUDA_VISIBLE_DEVICES"]})
    with (directory / "launcher.log").open("x") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    ready_deadline = time.time() + min(c.read(c.ROOT / "RECIPE.json")["caps"]["service_ready"], remaining(deadline))
    try:
        while time.time() < ready_deadline:
            claim_service(service)
            if process.poll() is not None:
                if process.returncode or not (service / "SERVER_READY.json").exists():
                    raise RuntimeError("owned service launcher failed; see retained log")
                return binding_path, service / "endpoint-original.json"
            time.sleep(.5)
        raise TimeoutError("service readiness cap180s reached")
    except BaseException:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGINT)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=10)
        stop_service(service)
        raise


def owned_command(command, log_path, timeout, *, gpu=False):
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    if not gpu:
        environment["CUDA_VISIBLE_DEVICES"] = ""
    with log_path.open("x") as log:
        process = subprocess.Popen(command, env=environment, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        result = process.wait(timeout=timeout)
    except BaseException:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGINT)
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=10)
        raise
    if result:
        raise RuntimeError(f"owned subprocess exit{result}; retained log {log_path}")


def stage(directory, phase, binding, endpoint, deadline, stage_cap, generation=None):
    if (directory / "export/MANIFEST.json").exists():
        native.authenticate_export(directory / "export")
        return c.read(directory / "export/MANIFEST.json")
    if directory.exists():
        # A completed rollout can be exported after a coordinator interruption; no model rerun.
        if not (directory / "rollout/STATUS.json").exists():
            raise ValueError("incomplete collection stage retained; no implicit retry")
        status = c.read(directory / "rollout/STATUS.json")
        if status["recorded"] != status["planned"] or status["stop_reason"] is not None:
            raise ValueError("collection stopped or capped; campaign must stop")
    else:
        directory.mkdir(parents=True)
        spec_path = directory / "CAPTURE_SPEC.json"
        cap = min(stage_cap, remaining(deadline))
        native.prepare_spec(phase, binding, endpoint, spec_path, cap, generation)
        command = [str(c.NATIVE_PYTHON), str(c.ROOT / "campaign_native.py"), "collect", "--spec", str(spec_path), "--output", str(directory / "rollout")]
        owned_command(command, directory / "collection.log", min(cap + 30, remaining(deadline) + 30))
        status = c.read(directory / "rollout/STATUS.json")
        if status["recorded"] != status["planned"] or status["stop_reason"] is not None:
            raise ValueError("collection reached termination/resource cap; no update from capped generation")
    manifest = native.export(directory / "rollout", directory / "export")
    if manifest["integrity_failures"]:
        raise ValueError("native role/mask/token integrity failure; evidence retained")
    if generation is not None and not manifest["training_group_episodes"]:
        raise ValueError("no mixed fresh within-task training group; no update")
    return manifest


def committed_policies(run):
    policies = {0: c.original_policy()}
    steps = []
    for directory in sorted(run.glob("round-*")):
        if not (directory / "GENERATION.json").exists():
            continue
        generation = c.read(directory / "GENERATION.json")
        step = generation["round"]
        state = directory / "training" / f"checkpoint-{step}" / "state.json"
        if not state.exists():
            continue
        if step - 1 not in policies:
            raise ValueError("checkpoint chain is not contiguous")
        c.check_generation(generation, policies[step - 1], step - 1)
        input_binding = c.read(state)["input_identity"]["input_binding"]
        expected_group = directory / "collection/export/GROUP.json"
        if (Path(input_binding["group_path"]).resolve() != expected_group.resolve()
                or input_binding["group_sha256"] != c.file_hash(expected_group)
                or input_binding["generation"] != generation
                or input_binding["campaign_sha256"] != c.file_hash(c.ROOT / "CAMPAIGN.json")):
            raise ValueError("checkpoint does not bind this exact round export/campaign")
        policy = c.checkpoint_policy(directory / "training", generation)
        commit = {"generation": generation, "policy": policy,
                  "checkpoint_state_sha256": policy["state_sha256"], "optimizer_steps": step}
        path = directory / "COMMIT.json"
        if path.exists() and c.read(path) != commit:
            raise ValueError("committed checkpoint changed")
        if not path.exists():
            c.write_once(path, commit)
        policies[step] = policy
        steps.append(step)
    c.contiguous_steps(steps)
    return policies


def run_campaign(args):
    manifest = c.verify_campaign()
    recipe = c.read(c.ROOT / "RECIPE.json")
    run = args.output.resolve()
    if not args.resume:
        run.mkdir(parents=True, exist_ok=False)
        started = time.time()
        c.write_once(run / "RUN.json", {"campaign_id": manifest["campaign_id"], "campaign_sha256": c.file_hash(c.ROOT / "CAMPAIGN.json"),
            "started_epoch": started, "deadline_epoch": started + recipe["caps"]["global"],
            "gpu": os.environ["CUDA_VISIBLE_DEVICES"]})
    run_info = c.read(run / "RUN.json")
    if run_info["campaign_sha256"] != c.file_hash(c.ROOT / "CAMPAIGN.json") or run_info["gpu"] != os.environ["CUDA_VISIBLE_DEVICES"]:
        raise ValueError("resume campaign/device identity changed")
    deadline = run_info["deadline_epoch"]
    # Resume only completed stages/checkpoints. Authenticate and stop any *owned* old service.
    for request in sorted(run.glob("services/*/SERVICE_REQUEST.json")):
        service = request.parent / "service"
        if not (request.parent / "SERVICE_STOPPED.json").exists():
            stop_service(service)
    policies = committed_policies(run)
    if (run / "FINAL.json").exists():
        return c.read(run / "FINAL.json")
    for old_stop in run.glob("STOP-*.json"):
        raise ValueError(f"terminal campaign stop retained at {old_stop}; no automatic retry or extra seeds")
    try:
        while max(policies) <= 8:
            step = max(policies)
            policy = policies[step]
            validation_path = run / f"validation-{step:02d}"
            need_validation = step in (0, 2, 4, 6, 8) and not (validation_path / "export/MANIFEST.json").exists()
            next_directory = run / f"round-{step + 1:02d}"
            need_rollout = step < 8 and not (next_directory / "collection/export/MANIFEST.json").exists()
            if need_rollout and not (next_directory / "collection").exists() and remaining(deadline) < recipe["caps"]["minimum_new_round_remaining"]:
                raise TimeoutError("fewer than15minutes remain; no new round")
            if step < 8:
                generation_path = next_directory / "GENERATION.json"
                plan = c.read(c.ROOT / "inputs/PLANS.json")["training"][str(step + 1)]
                generation = c.generation_identity(manifest["campaign_id"], step + 1, policy, c.digest(plan))
                if generation_path.exists() and c.read(generation_path) != generation:
                    raise ValueError("stale per-round generation manifest")
                if not generation_path.exists():
                    c.write_once(generation_path, generation)
            if need_validation or need_rollout:
                service_dir = run / "services" / f"step-{step:02d}-{uuid.uuid4().hex[:8]}"
                binding, endpoint = start_service(service_dir, policy, deadline)
                try:
                    if need_validation:
                        stage(validation_path, f"validation-{step}", binding, endpoint, deadline, recipe["caps"]["validation"])
                    if need_rollout:
                        if not (next_directory / "collection").exists() and remaining(deadline) < recipe["caps"]["minimum_new_round_remaining"]:
                            raise TimeoutError("validation consumed new-round reserve; fewer than15minutes remain")
                        stage(next_directory / "collection", f"round-{step + 1}", binding, endpoint, deadline, recipe["caps"]["collection"], generation)
                finally:
                    stop_service(service_dir / "service")
            if step == 8:
                break
            export = next_directory / "collection/export"
            native.authenticate_export(export)
            if not (export / "GROUP.json").exists():
                raise ValueError("no fresh mixed group")
            if not ports_free():
                raise ValueError("inference still occupies owned ports; no co-resident training")
            command = [str(c.TRAIN_PYTHON), str(c.ROOT / "campaign_train.py"), "--group", str(export / "GROUP.json"),
                "--generation", str(generation_path), "--output", str(next_directory / "training"), "--deadline", str(deadline)]
            # Authentication has its own bounded CPU replay. Trainer enforces min600/global
            # load+optimization cap and disables it only for immediate completed-step serialization.
            owned_command(command, next_directory / "training.log", min(900, remaining(deadline) + 120), gpu=True)
            policies = committed_policies(run)
            if max(policies) != step + 1:
                raise ValueError("trainer exited without required valid checkpoint")
        validations = []
        for step in (0, 2, 4, 6, 8):
            export = run / f"validation-{step:02d}/export"
            native.authenticate_export(export)
            result = c.read(export / "MANIFEST.json")
            validations.append({"step": step, "strict_successes": result["strict_successes"],
                "planned": 8, "admitted_outcomes": result["admitted_outcomes"], "manifest_sha256": c.file_hash(export / "MANIFEST.json")})
        selected = min(validations, key=lambda row: (-row["strict_successes"], row["step"]))["step"]
        selection = {"policy": policies[selected], "selected_step": selected, "validation": validations,
                     "rule": "earliest maximum strict successes over fixed8; excluded failures reported separately"}
        if not (run / "SELECTION.json").exists():
            c.write_once(run / "SELECTION.json", selection)
        elif c.read(run / "SELECTION.json") != selection:
            raise ValueError("validation selection changed")
        transfer_clock = run / "TRANSFER_STARTED.json"
        if not transfer_clock.exists():
            c.write_once(transfer_clock, {"started_epoch": time.time(), "deadline_epoch": min(deadline, time.time() + recipe["caps"]["transfer"])})
        transfer_deadline = c.read(transfer_clock)["deadline_epoch"]
        for condition, policy in [("original", policies[0]), ("selected", policies[selected])]:
            directory = run / f"transfer-{condition}"
            if (directory / "export/MANIFEST.json").exists():
                native.authenticate_export(directory / "export")
                continue
            service_dir = run / "services" / f"transfer-{condition}-{uuid.uuid4().hex[:8]}"
            binding, endpoint = start_service(service_dir, policy, transfer_deadline)
            try:
                stage(directory, f"transfer-{condition}", binding, endpoint, transfer_deadline, remaining(transfer_deadline))
            finally:
                stop_service(service_dir / "service")
        result = {"status": "complete", "optimizer_steps": max(policies), "selection": selection,
                  "final_policy": policies[8], "elapsed_seconds": time.time() - run_info["started_epoch"],
                  "transfer": {condition: c.read(run / f"transfer-{condition}/export/MANIFEST.json") for condition in ("original", "selected")}}
        c.write_once(run / "FINAL.json", result)
        return result
    except BaseException as error:
        policies = committed_policies(run)  # Recover a valid saved step even if subprocess/report failed.
        # A valid checkpoint saved just before an orchestration interruption is resumable.
        # Terminal numerical/data/resource failures without a new commit remain terminal.
        recovered_step = max(policies) > step
        stopped = {"status": "stopped", "type": type(error).__name__, "reason": str(error),
            "optimizer_steps": max(policies), "last_policy": policies[max(policies)],
            "checkpoint_recovered_after_error": recovered_step,
            "elapsed_seconds": time.time() - run_info["started_epoch"], "traceback": traceback.format_exc()}
        prefix = "INTERRUPTED_AFTER_COMMIT" if recovered_step else "STOP"
        c.write_once(run / f"{prefix}-{uuid.uuid4().hex}.json", stopped)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "run", "resume"))
    parser.add_argument("--output", type=Path, default=c.ROOT / "outputs/attempt-001")
    args = parser.parse_args()
    if args.command == "verify":
        print(json.dumps({"campaign_id": c.verify_campaign()["campaign_id"], "gpu_calls": 0}))
    else:
        if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:
            raise ValueError("parent must explicitly assign one exclusively owned GPU")
        args.resume = args.command == "resume"
        # The coordinator lease excludes a second instance, including across output directories.
        with (c.ROOT / "COORDINATOR.lock").open("a") as lease:
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            print(json.dumps(run_campaign(args), sort_keys=True))
