"""Additive Prime-title/owned-worker lifecycle fix; all sealed V1 research code stays intact."""

import argparse
import fcntl
import json
import os
import signal
import time
from pathlib import Path

import campaign as v1
import campaign_common as c
import campaign_native as native

AMENDMENT = c.ROOT / "LIFECYCLE_V2.json"
V1_CAMPAIGN_SHA = "8ea80a8f8ebbc48eebe7816e121d6ee32b1d3cd2d17ce4c069e0c47383f57c2f"
ORIGINAL_BINDING = native.binding_for
ORIGINAL_PREPARE = native.prepare_spec
PRIME_TITLE = "PRL::Inference"


def verify_amendment():
    c.verify_campaign()
    c.authenticate({c.ROOT / "CAMPAIGN.json": V1_CAMPAIGN_SHA})
    value = c.read(AMENDMENT)
    if c.digest({k: v for k, v in value.items() if k != "amendment_id"}) != value["amendment_id"]:
        raise ValueError("lifecycle amendment identity changed")
    c.authenticate(value["source_sha256"])
    return value


def observe(pid):
    value = v1.process_identity(pid)
    if value is None:
        return None
    boot = next(int(line.split()[1]) for line in Path("/proc/stat").read_text().splitlines() if line.startswith("btime "))
    value["started_epoch"] = boot + value["start_ticks"] / os.sysconf("SC_CLK_TCK")
    return value


def same_process(expected, actual):
    return actual is not None and all(actual.get(k) == expected.get(k) for k in ("pid", "uid", "pgid", "start_ticks"))


def validate_start_observation(actual, start, command):
    if actual is None or actual["pid"] != start["pid"] or actual["uid"] != os.getuid() or actual["pgid"] != actual["pid"]:
        raise ValueError("owned launcher PID/uid/group identity mismatch")
    if not -1 <= start["started"] - actual["started_epoch"] <= 10:
        raise ValueError("SERVER_START timestamp does not match actual process start")
    argv = [arg.strip() for arg in actual["argv"] if arg.strip()]
    if argv[-len(command):] != command and argv != [PRIME_TITLE]:
        raise ValueError("process command/title is not the exact launcher or known Prime title")
    return True


def safe_observation(actual):
    return {**{k: actual[k] for k in ("pid", "uid", "pgid", "start_ticks", "started_epoch")},
            "argv_sha256": c.digest(actual["argv"]),
            "known_prime_title": [arg.strip() for arg in actual["argv"] if arg.strip()] == [PRIME_TITLE]}


def live_owned(records, observer=observe):
    live = []
    for record in records:
        actual = observer(record["pid"])
        if actual is None:
            continue
        if not same_process(record, actual):
            raise ValueError("owned process identity changed; refusing arbitrary PID signaling")
        live.append(record)
    return live


def snapshot_descendants(service, parent):
    """Observe only descendants of an authenticated owned process, never a broad cleanup scan."""
    import psutil
    actual = observe(parent["pid"])
    if actual is None:
        return
    if not same_process(parent, actual):
        raise ValueError("parent identity changed before descendant observation")
    try:
        children = psutil.Process(parent["pid"]).children(recursive=True)
    except psutil.NoSuchProcess:
        return
    for process in children:
        child = observe(process.pid)
        if child is None:
            continue
        if child["uid"] != parent["uid"]:
            raise ValueError("unexpected descendant UID; no broad cleanup authorized")
        path = service.parent / "OWNED_PROCESSES" / f"{child['pid']}-{child['start_ticks']}.json"
        if not path.exists():
            c.write_once(path, {"process": safe_observation(child), "observed_descendant_of": parent,
                "observed_epoch": time.time(), "amendment_sha256": c.file_hash(AMENDMENT)})


def claim_service(service):
    amendment = verify_amendment()
    owner_path = service.parent / "SERVICE_OWNER_V2.json"
    if owner_path.exists():
        owner = c.read(owner_path)
        if owner["amendment_sha256"] != c.file_hash(AMENDMENT):
            raise ValueError("owned service was created by a different lifecycle amendment")
        c.authenticate({service / "SERVER_START.json": owner["server_start_sha256"],
                        service / "BINDING.json": owner["binding_sha256"],
                        service.parent / "SERVICE_REQUEST.json": owner["request_sha256"]})
        snapshot_descendants(service, owner["process"])
        return owner
    if not (service / "SERVER_START.json").exists():
        return None
    start, request = c.read(service / "SERVER_START.json"), c.read(service.parent / "SERVICE_REQUEST.json")
    expected_command = [str(c.NATIVE_PYTHON.with_name("inference")), "@", str(service / "inference.json")]
    expected_launcher = [str(c.NATIVE_PYTHON), str(c.ROLE / "source/serve.py"), "--binding",
                         str(service.parent / "BINDING.json"), "--run-dir", str(service)]
    if (start["command"] != expected_command or request["command"] != expected_launcher
            or start["gpu"] != request["gpu"] or start["launcher_sha256"] != c.file_hash(c.ROLE / "source/serve.py")
            or c.read(service / "BINDING.json") != c.read(service.parent / "BINDING.json")):
        raise ValueError("SERVER_START/config/launcher binding does not authenticate this owned service")
    actual = observe(start["pid"])
    if actual is None:
        return None
    validate_start_observation(actual, start, expected_command)
    for path in (service / "inference.json", service / "inference.log"):
        path.chmod(0o600)
    owner = {"process": safe_observation(actual), "command": expected_command,
             "server_start_sha256": c.file_hash(service / "SERVER_START.json"),
             "binding_sha256": c.file_hash(service / "BINDING.json"),
             "request_sha256": c.file_hash(service.parent / "SERVICE_REQUEST.json"),
             "service": str(service), "amendment_id": amendment["amendment_id"],
             "amendment_sha256": c.file_hash(AMENDMENT)}
    c.write_once(owner_path, owner)
    snapshot_descendants(service, owner["process"])
    return owner


def owned_records(service, owner):
    records = {owner["process"]["pid"]: owner["process"]} if owner else {}
    for path in (service.parent / "OWNED_PROCESSES").glob("*.json"):
        record = c.read(path)
        if record["amendment_sha256"] != c.file_hash(AMENDMENT):
            raise ValueError("descendant ownership evidence changed amendment")
        value = record["process"]
        if value["pid"] in records and not same_process(records[value["pid"]], value):
            raise ValueError("duplicate owned PID with different start identity")
        records[value["pid"]] = value
    return list(records.values())


def stop_service(service):
    stopped = service.parent / "SERVICE_STOPPED.json"
    owner = claim_service(service)
    if owner is None and (service / "SERVER_START.json").exists():
        raise ValueError("service exited before ownership/worker proof; parent diagnosis required")
    records = owned_records(service, owner)
    if stopped.exists():
        if live_owned(records) or not v1.ports_free():
            raise ValueError("owned worker/ports still live despite previous release record")
        return
    for sig, seconds in ((signal.SIGINT, 30), (signal.SIGTERM, 20), (signal.SIGKILL, 10)):
        for record in live_owned(records):
            snapshot_descendants(service, record)
        records = owned_records(service, owner)
        active = live_owned(records)
        if not active:
            break
        # The parent process group is fixed by its start_new_session launch. A known title
        # change is not an identity change. Detached descendants are signaled individually.
        if owner and owner["process"] in active:
            actual = observe(owner["process"]["pid"])
            validate_start_observation(actual, c.read(service / "SERVER_START.json"), owner["command"])
            os.killpg(owner["process"]["pgid"], sig)
        if sig != signal.SIGINT:
            for record in live_owned(records):
                if not owner or record["pid"] != owner["process"]["pid"]:
                    os.kill(record["pid"], sig)
        until = time.monotonic() + seconds
        while time.monotonic() < until and live_owned(records):
            time.sleep(.2)
    if live_owned(records):
        raise RuntimeError("owned inference worker still running; training cannot start")
    if not v1.ports_free():
        raise RuntimeError("ports occupied after owned worker release; no unrelated cleanup")
    c.write_once(stopped, {"stopped_at": time.time(), "amendment_sha256": c.file_hash(AMENDMENT),
        "observed_owned_processes": records, "all_owned_process_identities_exited": True, "ports_free": True,
        "release_basis": "all captured owned parent/descendant identities gone, not merely closed API ports"})


def binding_for(policy):
    amendment = verify_amendment()
    return {**ORIGINAL_BINDING(policy), "execution_amendment": {"id": amendment["amendment_id"],
        "path": str(AMENDMENT), "sha256": c.file_hash(AMENDMENT), "entrypoint_sha256": c.file_hash(Path(__file__))}}


def prepare_spec(phase, binding_path, endpoint_path, destination, cap, generation=None):
    amendment = verify_amendment()
    baseline = destination.with_name("CAPTURE_SPEC_V1_BASE.json")
    spec = ORIGINAL_PREPARE(phase, binding_path, endpoint_path, baseline, cap, generation)
    spec["source_file_sha256"].update(amendment["source_sha256"])
    spec["source_file_sha256"][str(AMENDMENT)] = c.file_hash(AMENDMENT)
    spec["execution_amendment"] = {"id": amendment["amendment_id"], "sha256": c.file_hash(AMENDMENT),
        "baseline_spec_sha256": c.file_hash(baseline), "entrypoint": str(Path(__file__).resolve())}
    c.write_once(destination, spec)
    return spec


def install():
    verify_amendment()
    v1.claim_service, v1.stop_service = claim_service, stop_service
    native.binding_for, native.prepare_spec = binding_for, prepare_spec


def run(args):
    amendment = verify_amendment()
    campaign = c.verify_campaign()
    output = args.output.resolve()
    if args.command == "run":
        output.mkdir(parents=True, exist_ok=False)
        started = time.time()
        c.write_once(output / "RUN.json", {"campaign_id": campaign["campaign_id"], "campaign_sha256": V1_CAMPAIGN_SHA,
            "started_epoch": started, "deadline_epoch": started + c.read(c.ROOT / "RECIPE.json")["caps"]["global"],
            "gpu": os.environ["CUDA_VISIBLE_DEVICES"]})
        c.write_once(output / "EXECUTION_V2.json", {"amendment_id": amendment["amendment_id"],
            "amendment_sha256": c.file_hash(AMENDMENT), "entrypoint_sha256": c.file_hash(Path(__file__)),
            "run_sha256": c.file_hash(output / "RUN.json"), "original_v1_seal_preserved": True})
    execution = c.read(output / "EXECUTION_V2.json")
    if execution["amendment_sha256"] != c.file_hash(AMENDMENT) or execution["entrypoint_sha256"] != c.file_hash(Path(__file__)):
        raise ValueError("resume executed lifecycle source differs")
    c.authenticate({output / "RUN.json": execution["run_sha256"]})
    install()
    # V2 creates the exact authenticated RUN envelope before entering the unchanged state machine.
    return v1.run_campaign(argparse.Namespace(output=output, resume=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "run", "resume"))
    parser.add_argument("--output", type=Path, default=c.ROOT / "outputs/attempt-v2-001")
    args = parser.parse_args()
    if args.command == "verify":
        print(json.dumps({"amendment_id": verify_amendment()["amendment_id"], "gpu_calls": 0}))
    else:
        if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:
            raise ValueError("parent must assign one exclusively owned device")
        with (c.ROOT / "COORDINATOR.lock").open("a") as lease:
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            print(json.dumps(run(args), sort_keys=True))
