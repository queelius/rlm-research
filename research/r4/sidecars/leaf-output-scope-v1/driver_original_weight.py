"""Explicit original-weight intervention over frozen scope72; no server ownership."""
from __future__ import annotations

import argparse
import asyncio
from copy import deepcopy
from pathlib import Path

import driver as v1
import study

ROOT = study.ROOT
ADAPTER = ROOT.parent / 'single-gpu-self-sft-control-v1/inputs/step0-peft-key-conversion-v2'
SHA = '857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6'
CONFIG_SHA = 'e6828a7cbb97028a871958e71ba6b8a75ac4887c25008ac4dbf7366bd298fbc4'
CONVERSION_SHA = '428f0241a075977fa02fc3c315fad39a21bb1e02a31d26b0ff47e49c6c8d15ba'
SOURCES = {'driver.py': 'af2ba1a2e196221b3d35fe832865ec99bf17d6789b1f4906e44f4cf9bcc6123a',
           'study.py': '933517e6f0b26d5257a1db8c31bdaad312f5fe97398b03f68a1bd5fb0340a6f2',
           'SPEC.json': 'f56d0b83685fd0f7ed2b6b2acee07c8decfd35ee5483860b14faf5c1cb909773'}
OUTPUT = ROOT / 'outputs/attempt-original-weight-001'


def authenticate_sources():
    for name, expected in SOURCES.items():
        if study.file_hash(ROOT / name) != expected:
            raise ValueError('frozen scope source changed: ' + name)
    if study.file_hash(ADAPTER / 'CONVERSION.json') != CONVERSION_SHA:
        raise ValueError('exact original tensor conversion proof changed')
    proof = study.read(ADAPTER / 'CONVERSION.json')
    if (proof['destination_adapter_sha256'] != SHA or proof['source_tensor_count'] != 504
            or not proof['cpu_load_validation']['all_tensor_values_and_dtypes_equal']):
        raise ValueError('original conversion is not the qualified exact504 tensor binding')


def validate_endpoint(descriptor):
    authenticate_sources()
    if descriptor.get('adapter') != {'path': str(ADAPTER), 'model_sha256': SHA, 'config_sha256': CONFIG_SHA}:
        raise ValueError('requires exact original converted adapter, not old/A/B weights')
    study.corr.leaf.verify_weights(descriptor)
    if (descriptor['base_model']['path'] != str(study.corr.BASE)
            or descriptor['base_model']['manifest_sha256'] != '19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f'
            or not descriptor.get('inference_only') or descriptor.get('status', '').startswith('planned')
            or descriptor.get('vllm', {}).get('version') != '0.28.0'
            or descriptor['vllm'].get('max_model_len', 0) < 8192
            or type(descriptor['port']) is not int or not 1024 <= descriptor['port'] <= 65535):
        raise ValueError('actual qualified local original descriptor required')


def validate_live_models(descriptor, response):
    cards = {r['id']: r for r in response['data']}
    card = cards.get(descriptor['model_alias'], {})
    if card.get('root') != str(ADAPTER) or card.get('parent') != str(study.corr.BASE):
        raise ValueError('live alias/root/base differs from exact original binding')
    if cards.get(str(study.corr.BASE), {}).get('max_model_len', 0) < 8192:
        raise ValueError('live base context limit changed')


def bind_identity(unbound, descriptor):
    validate_endpoint(descriptor)
    result = deepcopy(unbound)
    result['design']['model_alias'] = descriptor['model_alias']
    for key, body in result['requests'].items():
        body['model'] = descriptor['model_alias']
        if {**body, 'model': unbound['design']['model_alias']} != unbound['requests'][key]:
            raise ValueError('non-model request changed')
    result['request_sha256'] = {key: study.digest(body) for key, body in result['requests'].items()}
    result['weights'] = {'condition': 'original', 'adapter': deepcopy(descriptor['adapter']),
        'base_model': deepcopy(descriptor['base_model']), 'parent_weights_evidence': unbound['weights']}
    result['weight_amendment'] = {'question': 'Is scope/selection failure specific to the old trained child?',
        'intervention': 'original exact converted step0 instead of old c32de; model field only in provider requests',
        'parent_spec_sha256': SOURCES['SPEC.json'], 'executed_wrapper_sha256': study.file_hash(__file__),
        'reused_validation_and_seeds': True, 'no_new_independent_context_claim': True,
        'physical_input_caution': 'Preserve raw mismatch flags. vLLM typed tool serialization differs from frozen CPU tool-key order; actual captured IDs retained. No waiver or flag repair.'}
    paths = [Path(__file__), ROOT / 'test_original_weight.py', ROOT / 'ORIGINAL_WEIGHT_DESIGN.md',
             ADAPTER / 'CONVERSION.json', ADAPTER / 'adapter_model.safetensors', ADAPTER / 'adapter_config.json']
    result['source_file_sha256'].update({str(p): study.file_hash(p) for p in paths})
    return result


def correct_attempt(value):
    return {**value, 'adapter_sha256': SHA, 'weight_condition': 'original',
            'wrapper_sha256': study.file_hash(__file__), 'parent_collector': str(ROOT / 'driver.py')}


def install():
    # This CLI process owns private imports; no source or other process is altered.
    v1.bind_identity = bind_identity
    study.corr.validate_endpoint = validate_endpoint
    study.corr.validate_live_models = validate_live_models
    original_write = study.write_once

    def write(path, value):
        original_write(path, correct_attempt(value) if path.name == 'ATTEMPT.json' else value)
    study.write_once = write


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['seal', 'bind', 'run', 'verify'])
    parser.add_argument('--endpoint-descriptor', type=Path)
    parser.add_argument('--spec-path', type=Path, default=ROOT / 'BOUND-original-weight-attempt-001.json')
    parser.add_argument('--output-dir', type=Path, default=OUTPUT)
    args = parser.parse_args()
    authenticate_sources()
    install()
    if args.command == 'seal':
        v1.verify(study.read(ROOT / 'SPEC.json'))
        study.write_once(ROOT / 'ORIGINAL_WEIGHT_READY.json', {'status': 'READY_REQUIRES_AUTHENTICATED_ORIGINAL_ENDPOINT',
            'driver': str(Path(__file__).resolve()), 'driver_sha256': study.file_hash(__file__),
            'output': str(OUTPUT), 'spec': str(args.spec_path), 'parent_source_sha256': SOURCES,
            'test_sha256': study.file_hash(ROOT / 'test_original_weight.py'),
            'design_sha256': study.file_hash(ROOT / 'ORIGINAL_WEIGHT_DESIGN.md'),
            'adapter_sha256': SHA, 'conversion_sha256': CONVERSION_SHA,
            'focused_tests': 2, 'model_calls_during_preparation': 0, 'no_service_authority': True})
    elif args.command == 'bind':
        if args.endpoint_descriptor is None or args.spec_path == ROOT / 'SPEC.json':
            parser.error('bind requires actual descriptor and NEW spec path')
        v1.bind(args.endpoint_descriptor.resolve(), args.spec_path.resolve())
    elif args.command == 'verify':
        v1.verify(study.read(args.spec_path))
    else:
        spec = study.read(args.spec_path)
        if spec.get('weights', {}).get('condition') != 'original':
            raise ValueError('run requires explicit original-weight bound spec')
        raise SystemExit(asyncio.run(v1.run(args.spec_path.resolve(), args.output_dir.resolve())))


if __name__ == '__main__':
    main()
