"""Fresh coordinates, authentic final weights; unchanged qualified native collector."""
import argparse
import asyncio
import contextlib
import functools
import os
from pathlib import Path
from types import ModuleType

import study as s


def validate_descriptor(binding, descriptor, binding_sha):
    root = binding['models'][binding['role_map']['root']]
    if (descriptor['model_alias'] != binding['role_map']['root']
            or descriptor['adapter'] != {'path': root['path'], 'model_sha256': root['adapter_sha256'], 'config_sha256': root['config_sha256']}
            or descriptor['role_binding_sha256'] != binding_sha
            or descriptor['base_model']['manifest_sha256'] != s.BASE_SHA):
        raise ValueError('actual descriptor/root/base differs')


def validate_prefix(actual, expected, alias, wanted_alias):
    if actual != expected or alias != wanted_alias:
        raise ValueError('native physical prefix/alias differs')


def compose(plan, prompts):
    st = s.stack()
    original = s.read(s.PRIOR / 'prepared-v2/EVAL_PLAN_FINAL.json')
    frozen = {v['id']: v for v in s.read(s.PRIOR / 'prepared-v2/EVAL_PROMPTS.json')}
    if plan != s.build_plan(original) or len(prompts) != 24:
        raise ValueError('declared fresh plan/prefix set differs')
    for row, prompt in zip(plan, prompts):
        source = frozen[row['source_coordinate_id']]
        validate_prefix(prompt['token_ids'], source['token_ids'], prompt['id'], row['id'])
        if prompt['prompt'] != source['prompt']:
            raise ValueError('source prompt text differs')
    view = ModuleType('rowmean_readout_study_view')
    view.__dict__.update(st.prior.__dict__)
    replacements = {s.PRIOR / 'prepared-v2/EVAL_PLAN_FINAL.json': plan,
                    s.PRIOR / 'prepared-v2/EVAL_PROMPTS.json': prompts}
    view.read = lambda path: replacements[Path(path)] if Path(path) in replacements else st.prior.read(path)
    source = s.PRIOR / 'evaluate.py'
    with s.aliases({'study': view, 'native': st.native}):
        collector = s.load('rowmean_original_native_collector', source,
                           s.read(s.PRIOR / 'READY.json')['source_sha256'][str(source)])
    return collector, st


async def collect(args):
    import httpx
    ready = s.verify()
    if args.weight == 'global_target_token':
        if args.training.resolve() != s.CONTROL:
            raise ValueError('control training source changed')
        selected = s.checkpoint(s.CONTROL, s.PRIOR_IDENTITY, s.CONTROL_SHA)
    else:
        if args.training.resolve() != s.ROOT / 'outputs/attempt-001/training':
            raise ValueError('treatment is not the new fixed-final4 attempt')
        selected = s.checkpoint(args.training.resolve(), ready['identity'])
    binding, descriptor = s.read(args.binding), s.read(args.endpoint)
    s.validate_binding(binding, args.weight, args.training.resolve(), selected)
    validate_descriptor(binding, descriptor, s.sha(args.binding))
    with httpx.Client(trust_env=False, timeout=15, headers={'Authorization': 'Bearer ' + os.environ[descriptor['api_key_env']]}) as client:
        response = client.get(f'http://{descriptor["host"]}:{descriptor["port"]}/v1/models')
        response.raise_for_status()
        cards = {row['id']: row for row in response.json()['data']}
    for alias, model in binding['models'].items():
        if (cards.get(alias, {}).get('root') != model['path']
                or cards[alias].get('parent') != descriptor['base_model']['path']):
            raise ValueError('actual /models alias/path/base differs')
    plan, prompts = s.read(s.ROOT / 'prepared/PLAN.json'), s.read(s.ROOT / 'prepared/PROMPTS.json')
    collector, st = compose(plan, prompts)
    with s.aliases({'interface': st.interface}):
        interface = st.local.configure_interface(args.output)
    @contextlib.contextmanager
    def child_hooks(recipe, current_binding, output, current_plan, public):
        if recipe['child_interface']['kind'] != 'typed_batch' or recipe['child_interface']['pins'] != interface.PINS:
            raise ValueError('same typed child contract required')
        with interface.installed(current_binding, output, current_plan, public):
            yield interface
    collector.child_hooks = child_hooks
    s.write(args.output.parent / 'READOUT_BINDING.json',
            {'identity': ready['identity'], 'arm': args.weight, 'training_result_sha256': s.sha(args.training / 'RESULT.json'),
             'binding_sha256': s.sha(args.binding), 'descriptor_sha256': s.sha(args.endpoint),
             'models': cards, 'plan_sha256': s.sha(s.ROOT / 'prepared/PLAN.json'),
             'source_coordinate_crosswalk': {row['id']: row['source_coordinate_id'] for row in plan}})
    # The original collector checks the actual first wire prefix/alias against the
    # frozen replacements above, and writes raw/censored/unrun status unchanged.
    return await collector.collect(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weight', choices=s.PHASES, required=True)
    parser.add_argument('--training', type=Path, required=True)
    parser.add_argument('--binding', type=Path, required=True)
    parser.add_argument('--endpoint', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--deadline', type=float, required=True)
    raise SystemExit(asyncio.run(collect(parser.parse_args())))
