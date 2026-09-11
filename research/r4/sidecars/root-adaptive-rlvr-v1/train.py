"""Unchanged qualified loss/load/Adam/checkpoint code; exact fresh16 native proof seam."""
import argparse
import ast
import json
import traceback
import uuid
from pathlib import Path

import study as s
from common import c, starting_decision

SOURCE = s.CAMPAIGN / 'campaign_train.py'
with s.aliases({'campaign_common': c}):
    impl = s.load('adaptive_rlvr_train_impl', SOURCE, s.PINS[SOURCE])

# Only the authenticated group admission function needs the new collection size
# and verifier entrypoint. The actual optimizer/loss/load/save functions are reused.
node = next(n for n in ast.parse(SOURCE.read_text()).body
            if isinstance(n, ast.FunctionDef) and n.name == 'authenticate_group')
counts = {'size': 0, 'entrypoint': 0}
for item in ast.walk(node):
    if isinstance(item, ast.Constant) and type(item.value) is int and item.value == 32:
        item.value = 16
        counts['size'] += 1
    elif isinstance(item, ast.Constant) and item.value == 'campaign_native.py':
        item.value = 'native.py'
        counts['entrypoint'] += 1
if counts != {'size': 2, 'entrypoint': 1}:
    raise ValueError('qualified fresh-group adaptation seam changed')
exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE) + ':adaptive-fresh16', 'exec'), impl.__dict__)
base_authenticate_group = impl.authenticate_group


def authenticate_group(group_path, generation_path):
    starting_decision()  # Fresh start is bound even after generation1.
    group, generation, identity = base_authenticate_group(group_path, generation_path)
    rows = s.read(group_path.parent / 'EPISODES.json')
    if len(rows) != 16 or len({r['task_id'] for r in rows}) != 2:
        raise ValueError('exactly sixteen attempts from two frozen prompts required')
    for row in group['episodes']:
        if row.get('qualification_only') or row.get('generation_id') != generation['generation_id']:
            raise ValueError('qualification or stale likelihood cannot enter scientific training')
        for turn in row['turns']:
            if turn.get('typed_wire_grammar') is not False:
                raise ValueError('root current action unexpectedly grammar-constrained')
            s.check(turn['typed_audit_path'], turn['typed_audit_sha256'])
    # Preserve the inherited identity schema; explicit start is already in role_binding.
    return group, generation, identity


impl.authenticate_group = authenticate_group


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--group', type=Path, required=True)
    parser.add_argument('--generation', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--deadline', type=float, default=float('inf'))
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(impl.train(args), sort_keys=True, allow_nan=False))
    except BaseException as error:
        if args.output is not None:
            c.write_once(args.output.parent / ('TRAIN_FAILURE-' + uuid.uuid4().hex + '.json'),
                         {'type': type(error).__name__, 'error': str(error),
                          'traceback': traceback.format_exc(), 'checkpoint_preserved': True})
        raise


if __name__ == '__main__':
    main()
