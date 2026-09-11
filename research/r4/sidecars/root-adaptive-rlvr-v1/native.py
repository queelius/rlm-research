"""Exact native root-only turns with explicit typed-child wire evidence."""
import argparse
import functools
import json
import sys
from types import SimpleNamespace

import study as s


@functools.lru_cache(maxsize=1)
def stack():
    prior = s.prior_study()
    sources = s.read(s.PRIOR / 'READY.json')['source_sha256']
    with s.aliases({'study': prior}):
        native = s.load('adaptive_rlvr_original_native', s.PRIOR / 'native.py', sources[str(s.PRIOR / 'native.py')])
        interface = s.load('adaptive_rlvr_original_interface', s.PRIOR / 'interface.py', sources[str(s.PRIOR / 'interface.py')])
    # n.task copies this immutable prototype before assigning each exact public
    # context/prompt/gold. Avoid rebuilding all historical prototype tasks per slot.
    native.e.fixture_task = functools.lru_cache(maxsize=1)(native.e.fixture_task)
    local = s.load('adaptive_rlvr_local_runtime', s.LOCAL / 'adapter.py', s.PINS[s.LOCAL / 'adapter.py'])
    sys.path.insert(0, str(s.SIDE / 'root-only-credit-v1'))
    exporter_path = s.SIDE / 'root-only-credit-v1/root_export.py'
    exporter = s.load('adaptive_rlvr_exact_root_export', exporter_path,
                      '70f8bc7e9897dbdfc6ac14179db476d3d626c2a8e7fe5f9e835348276b7814b5')
    return SimpleNamespace(prior=prior, native=native, interface=interface, local=local, exporter=exporter)


def validate_typed_audit(audit):
    body = audit.get('native_wire_request', {}).get('body')
    if body is None:
        raise ValueError('typed invocation has no physical request')
    grammar = body['sampling_params'].get('structured_outputs')
    decision = audit['decision']
    if audit['depth'] == 0:
        if grammar is not None or decision['apply']:
            raise ValueError('root grammar must be absent for unrestricted root credit')
        return False
    if audit['depth'] != 1:
        raise ValueError('unexpected deeper role')
    expected = {'json': decision['schema']} if decision['apply'] else None
    if grammar != expected:
        raise ValueError('child grammar differs from recorded request-local decision')
    if grammar is not None:
        # Saved JSON sorts dict keys. The ordered string and pre-transport assertion
        # preserve the qualification seam; the saved body alone cannot prove order.
        ordered = decision['schema_ordered_json']
        if (json.loads(ordered) != grammar['json'] or audit.get('wire_schema_verified') is not True
                or __import__('hashlib').sha256(ordered.encode()).hexdigest() != decision['schema_ordered_sha256']):
            raise ValueError('child grammar ordered decision/pretransport proof differs')
    return grammar is not None


def exact_turns(episode, directory, binding, *, qualification=False):
    """No generation or retokenization; current action suffixes come from WireTrace."""
    st = stack()
    roots, evidence = st.exporter.episode_turns(episode, directory, binding)
    typed = {}
    for path in (directory / 'typed-audit').glob('*-result.json'):
        audit = s.read(path)
        if audit['request_id'] in typed:
            raise ValueError('duplicate typed request identity')
        typed[audit['request_id']] = (audit, path)
    for turn in evidence:
        identifier = turn['role_audit']['request_id']
        audit, path = typed[identifier]
        physical = s.read(turn['role_audit']['source_audit_path'])
        response = json.loads(physical['native_wire_response']['body'])
        request_id = str(response.get('request_id', ''))
        if not qualification and ('CPU' in request_id or 'fixture' in request_id.lower()):
            raise ValueError('qualification provider likelihood is not scientific RL data')
        if (audit['status'] != 'returned' or audit['depth'] != turn['role_depth']
                or audit['actual_alias'] != turn['call_model']
                or audit['native_wire_request']['body'] != physical['native_wire_request']['body']):
            raise ValueError('typed/native request-local evidence differs')
        turn['typed_wire_grammar'] = validate_typed_audit(audit)
        turn['typed_audit_path'] = str(path)
        turn['typed_audit_sha256'] = s.sha(path)
    # Same row objects remain shared by roots/evidence, preserving the checked ancestry.
    return roots, evidence


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('verify-export',))
    parser.add_argument('--output', type=__import__('pathlib').Path, required=True)
    args = parser.parse_args()
    from export import authenticate_export
    print(json.dumps(authenticate_export(args.output), sort_keys=True))
