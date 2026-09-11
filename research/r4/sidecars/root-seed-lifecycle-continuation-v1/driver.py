"""One explicit continuation of the saved independent-seed step6; no rerollouts."""
import argparse
import fcntl
import hashlib
import json
import os
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRIOR_ROOT = ROOT.parent / "root-rlvr-independent-seed-v1"
PRIOR_RUN = PRIOR_ROOT / "outputs/attempt-001"
PRIOR_READY_SHA = "c0391a4b8e973ab4bc74b9b4dac096bcdb89007ccaf9aa1d2863ea56f9c4866d"
STEP6_SHA = "53e822f25323040463ebf4e10f73ea69b4c68b00f612b8bc8de4b89c4b5cf3bb"
STOP_NAME = "STOP-cc892fb4815740428c22431ac943efc4.json"


def observe_or_absent(observer, pid):
    try:
        return observer(pid)
    except (FileNotFoundError, ProcessLookupError):
        return None


def inherited_names():
    return [f"round-{step:02d}" for step in range(1, 7)] + [
        f"validation-{step:02d}" for step in (0, 2, 4)
    ]


def run_envelope(started, gpu, campaign_id, campaign_sha):
    return {
        "campaign_id": campaign_id, "campaign_sha256": campaign_sha,
        "started_epoch": started, "deadline_epoch": started + 2880,
        "gpu": gpu, "inherited_optimizer_steps": 6,
        "inclusive_cap_seconds": 3000, "new_work_cap_seconds": 2880,
        "lifecycle_continuation_namespace": ROOT.name,
        "old_stop_preserved": True,
    }


def load_stack():
    ready_path = PRIOR_ROOT / "QUALIFIED_READY.json"
    if hashlib.sha256(ready_path.read_bytes()).hexdigest() != PRIOR_READY_SHA:
        raise ValueError("original qualification changed")
    ready = json.loads(ready_path.read_text())
    for name, expected in ready["source_sha256"].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != expected:
            raise ValueError("original qualified input/source changed: " + name)
    sys.path.insert(0, str(PRIOR_ROOT))
    import campaign_common as c
    import campaign as coordinator
    import campaign_native as native
    c.verify_campaign()
    native.install()
    return c, coordinator, native


def verify_prior(c, coordinator):
    stop = c.read(PRIOR_RUN / STOP_NAME)
    if stop["type"] != "ProcessLookupError" or stop["optimizer_steps"] != 6:
        raise ValueError("expected six-update lifecycle STOP missing")
    if (PRIOR_RUN / "round-07/collection").exists() or (PRIOR_RUN / "validation-06").exists():
        raise ValueError("remaining stage already has outputs; do not repeat it")
    policies = coordinator.impl.committed_policies(PRIOR_RUN)
    if max(policies) != 6 or policies[6] != stop["last_policy"] or policies[6]["adapter_sha256"] != STEP6_SHA:
        raise ValueError("not the exact committed six-update checkpoint chain")
    for step in (0, 2, 4):
        if not (PRIOR_RUN / f"validation-{step:02d}/export/MANIFEST.json").exists():
            raise ValueError("inherited completed validation missing")
    return policies


def install_observer_patch(coordinator):
    original = coordinator.impl.process_identity
    coordinator.impl.process_identity = lambda pid: observe_or_absent(original, pid)


def install_provenance(c, native, ready):
    original = native.prepare_spec

    def prepare_spec(phase, binding, endpoint, destination, cap, generation=None):
        baseline = destination.with_name("CAPTURE_SPEC_BEFORE_LIFECYCLE_NOTE.json")
        spec = original(phase, binding, endpoint, baseline, cap, generation)
        spec["source_file_sha256"].update(ready["source_sha256"])
        spec["source_file_sha256"][str(ROOT / "READY.json")] = c.file_hash(ROOT / "READY.json")
        spec["lifecycle_observation_continuation"] = {
            "namespace": ROOT.name, "prior_stop": str(PRIOR_RUN / STOP_NAME),
            "prior_stop_sha256": c.file_hash(PRIOR_RUN / STOP_NAME),
            "change": "vanished /proc process is absent; no model/objective/seed change",
            "baseline_spec_sha256": c.file_hash(baseline),
        }
        c.write_once(destination, spec)
        return spec

    native.prepare_spec = prepare_spec


def main():
    started = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/attempt-001")
    args = parser.parse_args()
    c, coordinator, native = load_stack()
    policies = verify_prior(c, coordinator)
    if args.command == "verify":
        print(json.dumps({"prior_steps": sorted(policies), "step6": policies[6],
            "next_stages": ["validation-06", "round-07", "round-08", "validation-08", "selection", "transfer"],
            "gpu_calls": 0}))
        return
    ready = c.read(ROOT / "READY.json")
    c.authenticate(ready["source_sha256"])
    c.authenticate(ready["input_sha256"])
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("main must assign one exclusive GPU and owned local service key")
    output = args.output.resolve()
    if output.parent != ROOT / "outputs" or output.exists():
        raise ValueError("new continuation output required")

    def hard_stop(sig, frame):
        raise TimeoutError("continuation3000-second inclusive exception cap or parent signal")

    for sig in (signal.SIGALRM, signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, hard_stop)
    signal.setitimer(signal.ITIMER_REAL, max(.001, 3000 - (time.time() - started)))
    with (ROOT / "COORDINATOR.lock").open("a") as lease:
        fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        output.mkdir(parents=True, exist_ok=False)
        manifest = c.read(PRIOR_ROOT / "CAMPAIGN.json")
        c.write_once(output / "RUN.json", run_envelope(started, gpu, manifest["campaign_id"], c.file_hash(PRIOR_ROOT / "CAMPAIGN.json")))
        mapping = []
        for name in inherited_names():
            source, target = PRIOR_RUN / name, output / name
            target.symlink_to(source, target_is_directory=True)
            mapping.append({"old": str(source), "new": str(target), "kind": "reference_only"})
        c.write_once(output / "INHERITED_STAGES.json", {"paths": mapping, "policies": policies,
            "prior_stop_sha256": c.file_hash(PRIOR_RUN / STOP_NAME), "ready_sha256": c.file_hash(ROOT / "READY.json"),
            "rerolled_episodes": 0, "reapplied_updates": 0, "old_stop_removed": False})
        install_observer_patch(coordinator)
        install_provenance(c, native, ready)
        try:
            result = coordinator.impl.run_campaign(argparse.Namespace(output=output, resume=True))
            print(json.dumps(result, sort_keys=True))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    main()
