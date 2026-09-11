"""Explicit immutable references for the exclusion-only continuation."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "root-rlvr-campaign-v1"
OLD_RUN = OLD / "outputs/attempt-v2-001"
OLD_ROUND04 = OLD_RUN / "round-04/collection/rollout"
CAP_SECONDS = 10800
STEP3_SHA = "6cd68cb764ea1dc46f2e0adf1a5d692d53ebc12cd5e5ef9d9c6dbd7d949fffcb"
if str(OLD) not in sys.path:
    sys.path.insert(0, str(OLD))
import campaign_common as c


def verify_amendment():
    value = c.read(ROOT / "AMENDMENT.json")
    if c.digest({k: v for k, v in value.items() if k != "amendment_id"}) != value["amendment_id"]:
        raise ValueError("continuation amendment identity changed")
    if value["namespace"] != ROOT.name or value["new_global_cap_seconds"] != CAP_SECONDS:
        raise ValueError("continuation namespace/budget changed")
    c.authenticate(value["source_sha256"])
    c.authenticate(value["input_sha256"])
    c.verify_campaign()
    return value


def prior_policies():
    prior = c.read(ROOT / "PRIOR.json")
    c.authenticate(prior["source_sha256"])
    policies = {0: c.original_policy()}
    for step in (1, 2, 3):
        directory = OLD_RUN / f"round-{step:02d}"
        generation = c.read(directory / "GENERATION.json")
        c.check_generation(generation, policies[step - 1], step - 1)
        policy = c.checkpoint_policy(directory / "training", generation)
        if policy != prior["policies"][str(step)] or c.read(directory / "COMMIT.json")["policy"] != policy:
            raise ValueError("original committed policy differs from fixed reference")
        policies[step] = policy
    if policies[3]["adapter_sha256"] != STEP3_SHA:
        raise ValueError("continuation is not the exact approved actualstep3")
    return policies
