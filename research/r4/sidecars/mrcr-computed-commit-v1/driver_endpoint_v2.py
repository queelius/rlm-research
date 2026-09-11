"""Additive host/port endpoint correction; frozen v1 protocol and scoring retained."""
from __future__ import annotations

import argparse
import asyncio
from collections import Counter
from pathlib import Path

import driver as v1
from study import ROOT, file_hash, read, write_once

ORIGINAL_SHA = '16ca882065dcd074bb9323a256100f397014d284720a4a4a70043d31364956c1'
ORIGINAL_CONTEXT = v1.context
DEFAULT_OUTPUT = ROOT / 'outputs/attempt-endpoint-v2-001'
AMENDMENT = ROOT / 'ENDPOINT_V2_AMENDMENT.json'


def context(endpoint, case):
    # Match the already-qualified native helper; do not change model/rendering/sampling.
    return ORIGINAL_CONTEXT({**endpoint, 'url': f"http://{endpoint['host']}:{endpoint['port']}/v1"}, case)


def operational_status(row):
    accounting = row['accounting']
    physical = accounting['physical_http_attempts']
    returned = accounting['observed_shared_execution']['returned_native_calls']
    called = physical > 0 or returned > 0
    pair = (row.get('captured') or {}).get('pair')
    failed = row['episode'].get('ok') is False or bool(row['episode'].get('errors'))
    if not called:
        status = 'setup_or_pre_call_failure' if failed else 'no_model_call'
    elif pair is not None:
        status = 'paired_submission'
    elif failed or returned == 0:
        status = 'model_called_runtime_or_budget_failure'
    else:
        status = 'model_non_submission'
    return {'status': status, 'model_called': called, 'physical_http_attempts': physical,
            'returned_native_calls': returned, 'model_non_submission': status == 'model_non_submission',
            'episode_errors': row['episode'].get('errors', [])}


async def run(endpoint, output):
    if file_hash(ROOT / 'driver.py') != ORIGINAL_SHA:
        raise ValueError('frozen v1 driver changed')
    amendment = read(AMENDMENT)
    for path, expected in amendment['source_sha256'].items():
        if file_hash(path) != expected:
            raise ValueError('endpoint amendment source changed: ' + path)
    v1.verify()
    if output.parent != ROOT / 'outputs' or output.exists():
        raise ValueError('new owned output required')
    statuses = {}
    original_run_case, original_write = v1.run_case, v1.write_once

    async def run_case(*args, **kwargs):
        row = await original_run_case(*args, **kwargs)
        status = operational_status(row)
        statuses[row['case']['index']] = status
        original_write(output / f"case-{row['case']['index']}" / 'OPERATIONAL.json', status)
        return row

    def write(path, value):
        if path.name == 'SCORE.json':
            operational = statuses[value['case']['index']]
            # Only status metadata changes; original official/exact metrics remain intact.
            value['v1_raw_status'] = value['status']
            value['operational'] = operational
            if value['status'] == 'non_submission':
                value['status'] = operational['status']
                value['v1_raw_restatement_outcome'] = value['restatement_outcome']
                value['restatement_outcome'] = {'classification': operational['status'], 'budget': None}
        elif path.name == 'RESULT.json':
            value['operational_counts'] = dict(Counter(item['status'] for item in statuses.values()))
            value['completed_coordinates_meaning'] = 'processed coordinates, not successful model completions'
            value['model_called_coordinates'] = sum(item['model_called'] for item in statuses.values())
            value['endpoint_amendment_sha256'] = file_hash(AMENDMENT)
        original_write(path, value)

    v1.context, v1.run_case, v1.write_once = context, run_case, write
    try:
        await v1.run(endpoint, output)
    except BaseException as error:
        output.mkdir(parents=True, exist_ok=True)
        original_write(output / 'OPERATIONAL_FAILURE.json', {
            'status': 'run_operational_failure', 'error_type': type(error).__name__, 'error': str(error),
            'case_statuses': statuses, 'no_performance_claim': True})
        raise
    finally:
        v1.context, v1.run_case, v1.write_once = ORIGINAL_CONTEXT, original_run_case, original_write
        if output.exists():
            original_write(output / 'ENDPOINT_V2_EXECUTION.json', {
                'amendment': amendment, 'amendment_sha256': file_hash(AMENDMENT),
                'actual_endpoint': str(endpoint), 'actual_endpoint_sha256': file_hash(endpoint),
                'driver_sha256': file_hash(__file__), 'prior_attempt': str(ROOT / 'outputs/attempt-001')})


def seal():
    v1.verify()
    previous = sorted((ROOT / 'outputs/attempt-001').glob('case-*/EPISODE.json'))
    assert len(previous) == 6
    assert all(operational_status(read(path))['status'] == 'setup_or_pre_call_failure' for path in previous)
    paths = [ROOT / 'driver.py', ROOT / 'SPEC.json', Path(__file__), ROOT / 'test_driver_endpoint_v2.py']
    write_once(AMENDMENT, {
        'schema': 'computed-commit-endpoint-v2', 'source_sha256': {str(p): file_hash(p) for p in paths},
        'prior_episode_sha256': {str(p): file_hash(p) for p in previous},
        'change': 'Only construct the native base_url from authenticated host/port; operational status metadata separates setup failures.',
        'unchanged': ['six development documents and seeds', 'gold/scoring', 'renderer', 'sampler', 'model binding', 'native capture', 'no retries'],
        'same_seeds_reason': 'All six prior episodes failed before model calls; preserved as setup evidence.',
        'cpu_test': '2 passed; actual descriptor regression was RED with KeyError(url) before amendment; no model calls.',
        'live_authentication': 'Inherited v1 authentication runs anew at launch; fixture descriptor is not live-service proof.'})
    write_once(ROOT / 'ENDPOINT_V2_READY.json', {
        'driver': str(Path(__file__).resolve()), 'driver_sha256': file_hash(__file__),
        'output': str(DEFAULT_OUTPUT), 'amendment_sha256': file_hash(AMENDMENT),
        'cli': 'python driver_endpoint_v2.py --endpoint ACTUAL --output NEW', 'gpu_calls_in_preparation': 0})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', type=Path)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--seal', action='store_true')
    args = parser.parse_args()
    if args.seal:
        seal()
    else:
        if args.endpoint is None:
            parser.error('--endpoint required')
        asyncio.run(run(args.endpoint.resolve(), args.output.resolve()))


if __name__ == '__main__':
    main()
