"""Private exact-lineage binding around the unchanged native physical collector."""
import argparse
import asyncio
import contextlib
import os
from pathlib import Path
import study as s
import binding as b


async def collect(args):
    import httpx
    ready = s.verify()
    if args.training.resolve() != b.training_source(args.weight):
        raise ValueError('arm training lineage path differs')
    chosen = b.selected(args.weight)
    binding, descriptor = s.read(args.binding), s.read(args.endpoint)
    if binding != b.binding(args.weight, chosen):
        raise ValueError('exact current root/child binding differs')
    b.validate_descriptor(binding, descriptor, s.sha(args.binding))
    with httpx.Client(trust_env=False, timeout=15, headers={'Authorization': 'Bearer ' + os.environ[descriptor['api_key_env']]}) as client:
        response = client.get(f'http://{descriptor["host"]}:{descriptor["port"]}/v1/models')
        response.raise_for_status()
        cards = {r['id']: r for r in response.json()['data']}
    for alias, model in binding['models'].items():
        if cards.get(alias, {}).get('root') != model['path'] or cards[alias].get('parent') != descriptor['base_model']['path']:
            raise ValueError('actual /models root/child/base differs')
    source = s.ROW / 'readout.py'
    with s.aliases({'study': s}):
        inherited = s.load('success_private_readout_crosswalk', source, 'f447b808a9c346ca1517442c798e3bce585ce8e65861d7c0df54f26789dd2a43')
    plan, prompts = s.read(s.ROOT / 'prepared/PLAN.json'), s.read(s.ROOT / 'prepared/PROMPTS.json')
    s.validate_prompts(plan, prompts)
    collector, st = inherited.compose(plan, prompts)
    def exact_binding(actual, arm, training):
        if (arm != args.weight or training.resolve() != args.training.resolve()
                or actual != binding):
            raise ValueError('private authenticated binding changed')
    collector.verify_binding = exact_binding
    with s.aliases({'interface': st.interface}):
        interface = st.local.configure_interface(args.output)
    @contextlib.contextmanager
    def hooks(recipe, actual, output, current_plan, public):
        if (actual != binding or current_plan != plan or recipe['child_interface']['kind'] != 'typed_batch'
                or recipe['child_interface']['pins'] != interface.PINS):
            raise ValueError('frozen native/typed contract changed')
        with interface.installed(actual, output, current_plan, public):
            yield interface
    collector.child_hooks = hooks
    s.write(args.output.parent / 'READOUT_BINDING.json', dict(identity=ready['identity'], arm=args.weight,
        binding_sha256=s.sha(args.binding), descriptor_sha256=s.sha(args.endpoint), models=cards,
        selected=chosen, plan_sha256=s.sha(s.ROOT / 'prepared/PLAN.json'),
        immutable_sources=[str(source), str(s.PRIOR / 'evaluate.py')],
        private_changes='exact three-arm binding and fresh coordinate crosswalk only'))
    return await collector.collect(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weight', choices=('baseline', 'success_sft', 'rl7'), required=True)
    for name in ('training', 'binding', 'endpoint', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--deadline', type=float, required=True)
    raise SystemExit(asyncio.run(collect(parser.parse_args())))
