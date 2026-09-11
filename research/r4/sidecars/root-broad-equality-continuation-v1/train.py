"""Unchanged broad16 trainer; only native-proof route and amendment provenance differ."""
import argparse
import importlib.util
import json
import subprocess
import types
from pathlib import Path

import common as a

c = a.c
loader = importlib.util.spec_from_file_location('equality_private_broad_train', a.BROAD / 'campaign_train.py')
broad = importlib.util.module_from_spec(loader)
loader.loader.exec_module(broad)
trainer = broad.trainer
ORIGINAL_AUTHENTICATE = trainer.authenticate_group
ORIGINAL_SUBPROCESS = trainer.subprocess


def native_proof_command(command):
    expected = [str(c.NATIVE_PYTHON), str(a.BROAD / 'campaign_native.py'), 'verify-export', '--output']
    if not isinstance(command, list) or len(command) != 5 or command[:4] != expected:
        raise ValueError('unexpected native proof command')
    return [command[0], str(a.ROOT / 'native.py'), *command[2:]]


def authenticate_group(group_path, generation_path):
    amendment = a.verify_amendment()
    manifest = c.read(Path(group_path).parent / 'MANIFEST.json')
    if manifest.get('equality_amendment', {}).get('id') != amendment['amendment_id']:
        raise ValueError('training requires exact equality export identity')
    def run_native(command, **kwargs):
        return subprocess.run(native_proof_command(command), **kwargs)
    trainer.subprocess = types.SimpleNamespace(run=run_native)
    try:
        group, generation, identity = ORIGINAL_AUTHENTICATE(group_path, generation_path)
    finally:
        trainer.subprocess = ORIGINAL_SUBPROCESS
    identity['equality_continuation'] = {'amendment_id': amendment['amendment_id'],
        'amendment_sha256': c.file_hash(a.ROOT / 'AMENDMENT.json'),
        'trainer_wrapper_sha256': c.file_hash(Path(__file__)), 'native_verifier': str(a.ROOT / 'native.py')}
    identity['input_identity'] = c.digest({k: v for k, v in identity.items() if k != 'input_identity'})
    return group, generation, identity


trainer.authenticate_group = authenticate_group


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--group', type=Path, required=True)
    parser.add_argument('--generation', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--deadline', type=float, default=float('inf'))
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    print(json.dumps(trainer.train(args), sort_keys=True, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
