"""Independent step0→8 using unchanged pinned coordinator; no automatic retries."""
import argparse
import fcntl
import json
import os
import signal
import sys
import time

import campaign_common as c

sys.modules["campaign"] = sys.modules[__name__]
impl = c.private("independent_seed_coordinator_original", c.OLD / "campaign.py")
_life = None


def __getattr__(name):
    return getattr(impl, name)


def lifecycle():
    global _life
    if _life is None:
        _life = c.private("campaign_lifecycle_v2", c.OLD / "campaign_lifecycle_v2.py")
        _life.V1_CAMPAIGN_SHA = c.file_hash(c.ROOT / "CAMPAIGN.json")
        _life.verify_amendment()
        impl.claim_service, impl.stop_service = _life.claim_service, _life.stop_service
    return _life


def main():
    entered = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["verify", "run"])
    parser.add_argument("--output", type=c.Path, default=c.ROOT / "outputs/attempt-001")
    args = parser.parse_args()
    c.verify_campaign()
    import campaign_native as native
    native.install()
    if args.command == "verify":
        print(json.dumps({"campaign_verified": True, "initial_binding": native.binding_for(c.original_policy()), "gpu_calls": 0}))
        return
    qualification = c.read(c.ROOT / "QUALIFIED_READY.json")
    if qualification["status"] != "CPU_READY_INDEPENDENT_SEED_ORIGINAL_STEP0":
        raise ValueError("CPU adapter qualification required")
    c.authenticate(qualification["source_sha256"])
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"] or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("main must assign one exclusively owned GPU and existing service key")
    if args.output.resolve().parent != c.ROOT / "outputs" or args.output.exists():
        raise ValueError("new own-namespace output required; no inherited attempt")
    def hard_stop(sig, frame):
        raise TimeoutError("independent seed inclusive6000-second hard cap or parent signal")
    signal.signal(signal.SIGALRM, hard_stop)
    signal.signal(signal.SIGTERM, hard_stop)
    signal.signal(signal.SIGINT, hard_stop)
    signal.setitimer(signal.ITIMER_REAL, max(.001, 6000 - (time.time() - entered)))
    with (c.ROOT / "COORDINATOR.lock").open("a") as lease:
        fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            print(json.dumps(impl.run_campaign(argparse.Namespace(output=args.output, resume=False)), sort_keys=True))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    main()
