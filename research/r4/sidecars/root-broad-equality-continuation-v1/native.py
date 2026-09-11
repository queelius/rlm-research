"""Exact child-context equality exclusion, preserving all original admission fields."""
import argparse
import ast
import asyncio
import json
import re
from pathlib import Path

import common as a

a.load_native_stack()
c, old, amended = a.c, a.base_native, a.BASE_AMENDED
ORIGINAL_VERIFY = amended.verify_failed_call
ORIGINAL_AUTHENTICATE = old.authenticate_export
ORIGINAL_PREPARE = old.prepare_spec
FULL_REJECTION = re.compile(r'The decoder prompt \(length (\d+)\) plus the number of requested output tokens \(at least 1\) is longer than the maximum model length of (\d+)\. Make sure that `max_model_len` is no smaller than the number of text tokens \(prompt \+ requested output tokens\)\.')
_source = (c.CONT / 'native_amendment.py').read_text()
_node = next(n for n in ast.parse(_source).body if isinstance(n, ast.FunctionDef) and n.name == 'verify_failed_call')
_function = ast.get_source_segment(_source, _node)
if _function.count('len(ids) <= 8192') != 1:
    raise ValueError('original exact length guard changed')
_function = _function.replace('len(ids) <= 8192', 'len(ids) != 8192')
_private = {**amended.__dict__, 'REJECTION': FULL_REJECTION}
exec(compile(_function, str(c.CONT / 'native_amendment.py') + ':equality-only', 'exec'), _private)
EQUALITY_VERIFY = _private['verify_failed_call']


def verify_failed_call(call, audit, binding, seed):
    try:
        return ORIGINAL_VERIFY(call, audit, binding, seed)
    except ValueError as error:
        if str(error) != 'not the explicit decoder-context overflow rejection':
            raise
    # Re-run every unchanged role/wire/sampling/no-completion check. No rewritten
    # call, response, token, logprob or reward is passed to either verifier.
    return EQUALITY_VERIFY(call, audit, binding, seed)


amended.verify_failed_call = verify_failed_call


def rebuild(attempt):
    amendment = a.verify_amendment()
    attempt = Path(attempt)
    spec = c.read(attempt / 'SPEC.json')
    inherited = attempt.resolve() == (a.PRIOR_RUN / 'round-01/collection/rollout').resolve()
    if not inherited and spec.get('equality_amendment', {}).get('id') != amendment['amendment_id']:
        raise ValueError('new capture lacks exact equality amendment identity')
    rows, group, manifest = amended.rebuild_export(attempt)
    manifest['equality_amendment'] = {'id': amendment['amendment_id'],
        'sha256': c.file_hash(a.ROOT / 'AMENDMENT.json'), 'inherited_round1': inherited,
        'rule': 'exact8192 child rejection plus unchanged>8192 rule; no new admission'}
    return rows, group, manifest


def export(attempt, output):
    rows, group, manifest = rebuild(attempt)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    c.write_once(output / 'EPISODES.json', rows)
    if group:
        c.write_once(output / 'GROUP.json', group)
    manifest['artifact_sha256'] = {p.name: c.file_hash(p) for p in output.iterdir()}
    c.write_once(output / 'MANIFEST.json', manifest)
    return manifest


def authenticate_export(output):
    output = Path(output)
    manifest = c.read(output / 'MANIFEST.json')
    if 'equality_amendment' not in manifest:
        expected = a.PRIOR_RUN / 'validation-00/export/MANIFEST.json'
        if c.file_hash(output / 'MANIFEST.json') != c.file_hash(expected):
            raise ValueError('only exact inherited validation0 may retain original export semantics')
        return ORIGINAL_AUTHENTICATE(output)
    c.authenticate({output / name: sha for name, sha in manifest['artifact_sha256'].items()})
    rows, group, rebuilt = rebuild(Path(manifest['source_attempt']))
    if rows != c.read(output / 'EPISODES.json') or rebuilt != {k: v for k, v in manifest.items() if k != 'artifact_sha256'}:
        raise ValueError('equality export differs from exact native evidence')
    if (group is None) != (not (output / 'GROUP.json').exists()) or group is not None and group != c.read(output / 'GROUP.json'):
        raise ValueError('mixed group differs from unchanged admission')
    return {'manifest_sha256': c.file_hash(output / 'MANIFEST.json'),
        'group_sha256': c.file_hash(output / 'GROUP.json') if group else None,
        'replayed': len(rows), 'selected': len(group['episodes']) if group else 0,
        'amendment_id': rebuilt['equality_amendment']['id'], 'verifier_source_sha256': c.file_hash(Path(__file__))}


def prepare_spec(phase, binding, endpoint, destination, cap, generation=None):
    amendment = a.verify_amendment()
    baseline = destination.with_name('CAPTURE_SPEC_BEFORE_EQUALITY_NOTE.json')
    spec = ORIGINAL_PREPARE(phase, binding, endpoint, baseline, cap, generation)
    spec['source_file_sha256'].update(amendment['source_sha256'])
    spec['source_file_sha256'].update(amendment['input_sha256'])
    spec['source_file_sha256'][str(a.ROOT / 'AMENDMENT.json')] = c.file_hash(a.ROOT / 'AMENDMENT.json')
    spec['equality_amendment'] = {'id': amendment['amendment_id'], 'baseline_spec_sha256': c.file_hash(baseline)}
    c.write_once(destination, spec)
    return spec


def install():
    old.export, old.authenticate_export, old.prepare_spec = export, authenticate_export, prepare_spec


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['collect', 'verify-export'])
    parser.add_argument('--spec', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    install()
    if args.command == 'collect':
        spec = old.impl.verify_spec(args.spec)
        if spec.get('equality_amendment', {}).get('id') != a.verify_amendment()['amendment_id']:
            raise ValueError('collector requires this exact equality amendment')
        result = asyncio.run(old.impl.collect(args.spec, args.output))
    else:
        result = authenticate_export(args.output)
    print(json.dumps(result, sort_keys=True, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
