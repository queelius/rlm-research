"""CPU native binding/task renderer plus trusted rootless fixture; never a model call."""
import argparse
import asyncio
import importlib.metadata
import json
import sys
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import campaign_common as c


def qualify(rootless=True):
    import campaign_native as native
    native.install()
    tasks=native.make_tasks()
    identity=native.task_identity(tasks)
    if identity!=c.read(c.ROOT/'inputs/TASK_IDENTITIES.json'):
        raise ValueError('task reconstruction changed')
    prior=set()
    def visit(value):
        if isinstance(value,dict):
            if type(value.get('seed')) is int: prior.add(value['seed'])
            for v in value.values(): visit(v)
        elif isinstance(value,list):
            for v in value: visit(v)
    for path in c.PINS:
        if path.name in ('PLAN.json','PLANS.json','SPEC_ORIGINAL.json'): visit(c.read(path))
    plans=c.read(c.ROOT/'inputs/PLANS.json')
    fresh={r['seed'] for rs in plans['training'].values() for r in rs}|{r['seed'] for r in plans['validation']+plans['transfer_original']}
    if len(fresh)!=448 or fresh&prior: raise ValueError('expanded prior root plan seed collision')
    c.write_once(c.ROOT/'qualification/SEED_AUDIT.json',{'fresh_unique_coordinates':448,'prior_unique_seed_values':len(prior),
        'collisions':0,'source_paths':[str(p) for p in c.PINS if p.name in ('PLAN.json','PLANS.json','SPEC_ORIGINAL.json')],
        'paired_transfer_and_repeated_validation_seed_reuse_intentional':True})
    binding=native.binding_for(c.original_policy())
    native.authenticate_binding(binding)
    if binding['campaign_policy']['step']!=0 or binding['models'][binding['fixed_child']]['adapter_sha256']!=c.CHILD_SHA:
        raise ValueError('original-root fixed-child binding changed')
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    renderer=create_renderer(load_tokenizer(c.pilot_recipe()['base_model']),Qwen3RendererConfig(enable_thinking=True))
    context_tokens={name:len(renderer._tokenizer.encode(t.data.context,add_special_tokens=False)) for name,t in tasks.items()}
    prompt_tokens={name:len(renderer._tokenizer.encode(native.capture.role.with_prompt(t,'sft_child').data.prompt,add_special_tokens=False)) for name,t in tasks.items()}
    # External context files need not fit a single model request; actual request cap remains8192.
    c.write_once(c.ROOT/'qualification/TASK_TOKEN_COUNTS.json',{'context_tokens':context_tokens,
        'public_question_with_definitions_tokens':prompt_tokens,'kind':'text-only tokenizer diagnostics, not full provider prompt IDs',
        'context_file_is_external':True,'forbidden_claim':'whole context256 automatically fits a child prompt'})
    result={'status':'CPU native task/binding/renderer qualified','tasks':len(tasks),'gpu_calls':0,
        'live_model_calls':0,'initial_binding':binding,'max_context_text_tokens':max(context_tokens.values()),
        'max_public_question_text_tokens':max(prompt_tokens.values()),'rootless_fixture':None,
        'python':sys.version,'versions':{n:importlib.metadata.version(n) for n in ['torch','transformers','peft','vllm','tokenizers']},
        'actual_source_transformations':c.TRANSFORMATIONS}
    if rootless:
        fixture=c.adapted('broad_native_trusted_fixture',c.PILOT/'qualify_native.py',[
            ('coordinate = read(ROOT / "inputs/PLAN.json")[0]',
             'coordinate = c.read(c.ROOT / "inputs/PLANS.json")["training"]["1"][0]',1)],{'c':c})
        capture=native.capture
        fixture.capture=capture
        capture.make_tasks=native.make_tasks
        capture.binding=lambda:binding
        capture.role.ORIGINAL=binding['role_map']['root']
        asyncio.run(fixture.qualify(c.ROOT/'qualification/native-rootless'))
        result['rootless_fixture']=c.read(c.ROOT/'qualification/native-rootless/RESULT.json')
    c.write_once(c.ROOT/'qualification/RESULT.json',result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--skip-rootless',action='store_true')
    args=parser.parse_args()
    with (c.ROOT/'qualification.stdout.log').open('x') as stdout, (c.ROOT/'qualification.stderr.log').open('x') as stderr:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result=qualify(not args.skip_rootless)
            print(json.dumps(result,sort_keys=True))
    print(json.dumps({'status':result['status'],'rootless':result['rootless_fixture'],'gpu_calls':0}))
