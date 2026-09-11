"""Private campaign cursor/checkpoint namespace; named warm start, fresh generation0."""
import functools
import os
from pathlib import Path

import study as s

c = s.load('adaptive_rlvr_common_impl', s.CAMPAIGN / 'campaign_common.py',
           s.PINS[s.CAMPAIGN / 'campaign_common.py'])
original_authenticate = c.authenticate_policy
c.ROOT, c.SEED = s.ROOT, s.SEED
c.verify_campaign = s.verify_prepared
c.pilot_math = functools.lru_cache(maxsize=1)(c.pilot_math)


def starting_decision():
    path = Path(os.environ['ADAPTIVE_RLVR_START_BINDING']).resolve()
    expected = os.environ['ADAPTIVE_RLVR_START_SHA256']
    s.check(path, expected)
    value = s.read(path)
    return path, value, s.authenticate_start(value)


def original_policy():
    return starting_decision()[2]


def authenticate_policy(policy):
    if policy['step'] == 0:
        if policy != original_policy():
            raise ValueError('campaign0 is not the MAIN-approved exact warm start')
        return
    original_authenticate(policy)


c.original_policy = original_policy
c.authenticate_policy = authenticate_policy
