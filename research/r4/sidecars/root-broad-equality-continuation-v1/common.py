"""Original broad16 stack and exact remaining-work continuation identity."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BROAD = ROOT.parent / 'root-broad-curriculum-v1'
PRIOR_RUN = BROAD / 'outputs/attempt-001'
STOP = PRIOR_RUN / 'STOP-118ee771bbdd4646a801f8dd2f7c73b8.json'
BROAD_READY_SHA = '94f416ebe6a613f4109a3648a177407f5567df574047cbb8a0e60a10ceec10a1'
STOP_SHA = '21dbe62c328f028f07b002e30409e20afe159f8c17f6cc57934a8b2df223f274'
PRIOR_SECONDS = 1170.5396137237549
WORK_SECONDS = 16829.460386276245
INCLUSIVE_SECONDS = 16949.460386276245
OUTER_SECONDS = 16980

if hashlib.sha256((BROAD / 'READY.json').read_bytes()).hexdigest() != BROAD_READY_SHA:
    raise ValueError('original broad READY changed')
_ready = json.loads((BROAD / 'READY.json').read_text())
for _name in ['campaign_common.py', 'campaign.py', 'campaign_native.py', 'campaign_train.py']:
    _path = BROAD / _name
    if hashlib.sha256(_path.read_bytes()).hexdigest() != _ready['source_sha256'][str(_path)]:
        raise ValueError('original broad source changed before import: ' + _name)
sys.path.insert(0, str(BROAD))
import campaign_common as c
sys.path.remove(str(BROAD))


def load_native_stack():
    global coordinator, base_native, BASE_AMENDED
    if 'BASE_AMENDED' in globals():
        return
    sys.path.insert(0, str(BROAD))
    try:
        import campaign as coordinator
        import campaign_native as base_native
        base_native.install()
    finally:
        sys.path.remove(str(BROAD))
    BASE_AMENDED = sys.modules['broad16_exclusion_original']


def verify_prior():
    c.authenticate({BROAD / 'READY.json': BROAD_READY_SHA, STOP: STOP_SHA})
    stop = c.read(STOP)
    if stop['optimizer_steps'] != 0 or stop['last_policy'] != c.original_policy() or stop['elapsed_seconds'] != PRIOR_SECONDS:
        raise ValueError('expected original root/emptyAdam STOP changed')
    if (PRIOR_RUN / 'round-01/training').exists() or (PRIOR_RUN / 'round-02').exists():
        raise ValueError('original run has later work; no duplicate continuation')
    status = c.read(PRIOR_RUN / 'round-01/collection/rollout/STATUS.json')
    if status['recorded'] != 24 or status['planned'] != 24 or status['stop_reason'] is not None:
        raise ValueError('requires complete saved24; no partial reroll')
    return stop


def verify_amendment():
    value = c.read(ROOT / 'AMENDMENT.json')
    if c.digest({k: v for k, v in value.items() if k != 'amendment_id'}) != value['amendment_id']:
        raise ValueError('equality amendment identity changed')
    c.authenticate(value['source_sha256'])
    c.authenticate(value['input_sha256'])
    verify_prior()
    return value
