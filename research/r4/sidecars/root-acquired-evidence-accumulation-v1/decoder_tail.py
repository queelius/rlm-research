# Appended to the exact frozen strict current-map validator; no task/gold input.
import time as _time
import hashlib as _hashlib

_decoded_state = {}
_decoder_commit = 0

def _ledger_value(value):
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return {'unserializable_type': type(value).__name__}

def _append_decoder_ledger(row):
    # Common, unadvertised, runtime-writable evidence, harvested after rollout.
    # Missing or tampered bookkeeping is not native source authentication.
    try:
        with open('.decoder_calls.jsonl', 'a', encoding='utf-8') as stream:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
    except (OSError, TypeError, ValueError):
        pass

def strict_map(raw, ids):
    global _decoder_commit
    _decoder_commit += 1
    row = dict(commit=_decoder_commit, started_epoch=_time.time(), raw=_ledger_value(raw),
               ids=_ledger_value(ids), raw_type=type(raw).__name__,
               raw_sha256=_hashlib.sha256(raw.encode()).hexdigest() if isinstance(raw, str) else None,
               genuine_child_provenance='not_established_by_decoder')
    try:
        current = _validate_current(raw, ids)
    except BaseException as error:
        row.update(ok=False, error=dict(type=type(error).__name__, message=str(error)), ended_epoch=_time.time())
        _append_decoder_ledger(row)
        raise
    conflicts = [dict(id=key, old=_decoded_state[key], new=value)
                 for key, value in current.items() if key in _decoded_state and _decoded_state[key] != value]
    _decoded_state.update(current)
    returned = dict(_decoded_state if _CUMULATIVE else current)
    row.update(ok=True, current=dict(current), returned=dict(returned), conflicts=conflicts,
               cumulative_ids=list(_decoded_state), ended_epoch=_time.time())
    _append_decoder_ledger(row)
    return returned
