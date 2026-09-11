"""Private pinned native dependencies and task/owned-engine binding."""
import contextlib
import hashlib
import importlib.util
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def checked_import(name, path, sha):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != sha:
        raise ValueError('source changed: '+str(path))
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prior = checked_import('adaptive_pinned_uptake', ROOT.parent/'root-receipt-uptake-v1/experiment.py',
                       '29df4de005ac7157149a3cfdca7730f001e0f3d2f5a4661b1e7acca81ea2a104')
c, capture, native, old = prior.c, prior.capture, prior.native, prior.old
sys.path.insert(0,str(ROOT))
from batch_contract import DEFINITIONS
from engine_adapter import overlay_program
from oolong_prime_rlm_strict_v1.taskset import StrictOolongTask


class AdaptiveTask(StrictOolongTask):
    async def setup(self, trace, runtime):
        await super().setup(trace,runtime)
        await runtime.write('batch_contract.py',(ROOT/'batch_contract.py').read_bytes())
        if self.controller!='free':
            await runtime.write('operator_program.py',(ROOT/'operator_program.py').read_bytes())
            await runtime.write('operator_config.json',json.dumps({'controller':self.controller}).encode())
        await runtime.write('records.json',json.dumps(self.public_records,ensure_ascii=False).encode())
        await runtime.write('query.txt',self.plain_query.encode())

    async def finalize(self, trace, runtime):
        await super().finalize(trace,runtime)
        try:
            payload=await runtime.read('operator_result.json',max_bytes=8*1024*1024)
            trace.info['operator_transcript']={'raw':payload.decode(),'sha256':hashlib.sha256(payload).hexdigest(),
                'trust':'runtime-writable transcript; corroborate native child capture and operator source'}
        except Exception as error:
            trace.info['operator_transcript']={'raw':None,'error_type':type(error).__name__,'message':str(error)}
        trace.info['controller_kind']='model' if self.controller=='free' else 'operator'
        trace.info['operator_root_behavior_likelihood']=None
        try:
            payload=await runtime.read('operator_native.json',max_bytes=1024*1024)
            trace.info['operator_native']={'raw':payload.decode(),'sha256':hashlib.sha256(payload).hexdigest()}
        except Exception as error:
            trace.info['operator_native']={'raw':None,'error_type':type(error).__name__}


def make_context(endpoint, row):
    return capture.make_context(endpoint,row)


def environment_config():
    import copy
    config=copy.deepcopy(c.read(c.PILOT/'SPEC.json')['environment'])
    config['agent']['timeout']={'setup':45.,'rollout':300.,'finalize':15.,'scoring':15.}
    return config


@contextlib.contextmanager
def installed_hooks(binding, output):
    from verifiers.v1.harnesses.rlm.harness import RLMHarness
    with capture.installed_hooks(binding,output):
        original=RLMHarness.setup
        async def setup(self,runtime):
            await original(self,runtime)
            program=overlay_program(capture.installed_hooks.__wrapped__.__globals__['role'])
            result=await runtime.run(['python','-c',program],{})
            c.write_once(output/'operator-overlays'/f'{uuid.uuid4().hex}.json',
                {'runtime':runtime.name,'program_sha256':hashlib.sha256(program.encode()).hexdigest(),
                 'exit_code':result.exit_code,'stdout':result.stdout,'stderr':result.stderr})
            if result.exit_code:
                raise RuntimeError('owned adaptive engine overlay failed')
        RLMHarness.setup=setup
        try: yield
        finally: RLMHarness.setup=original


def fixture_task(controller):
    original=next(iter(prior.make_tasks().values()))
    rows=[{'id':'q0001','user':'u00','text':'How many planets are there?'},
          {'id':'q0002','user':'u01','text':'What is the capital of France?'}]
    query='How many records in the entire file ask for a numeric value?'
    prompt='Use records.json and context.txt. '+DEFINITIONS+'\nReturn only Answer: N.\nQuestion: '+query
    task=AdaptiveTask(original.data.model_copy(update={'name':'adaptive-cpu-fixture','prompt':prompt,
        'context':json.dumps(rows),'answer':'1'}),original.config)
    task.public_records,task.plain_query,task.controller=rows,query,controller
    return task


def question(context, family):
    return ('How many records in the entire file ask for a numeric value?' if family=='global' else
            f'How many records from user {context["query_user"]} ask for a numeric value?')


def public_prompt(context, family):
    return ("The public file records.json contains a JSON list of128 records. Every record has an id, a synthetic user, and text containing the original question. context.txt is a readable copy of the same records. Users are synthetic metadata, not semantic labels. Count records, not distinct users. Numeric value means the category defined below.\n\n"
        + DEFINITIONS + "\nYou can use Python and ordinary await rlm(prompt) to ask a child for help. batch_contract.py contains a documented pure request builder and strict raw JSON decoder. Neither calls a model or chooses records for you. You may use them, write your own request, inspect original text yourself, choose subsets and batch sizes, or use another valid computation. No helper call or complete label map is required. Model labels may be wrong even when JSON is valid.\n\n"
        "Optional API example (only a starting batch, not the final answer):\n```python\nimport json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nrecords = json.load(open(\"records.json\"))\nbatch = records[:4]\nchild = await rlm(request_for(batch))\nlabels = strict_map(child.answer, [row[\"id\"] for row in batch])\nprint(labels)\n```\n\n"
        "request_for(batch) uses each record's id and original text, omitting user metadata. strict_map(raw, ids) rejects duplicate, missing or unknown IDs, non-object JSON, trailing text and labels outside the six definitions. It does not check semantic correctness or repair output. Return only Answer: N, where N is a nonnegative decimal integer.\n\nQuestion: "
        + question(context,family))


def make_tasks():
    from tokenizers import Tokenizer
    prototype=next(iter(prior.make_tasks().values()))
    tokenizer=Tokenizer.from_file(str(Path(c.pilot_recipe()['base_model'])/'tokenizer.json'))
    gold=c.read(ROOT/'inputs/HOST_GOLD.json')
    tasks={}
    for context in c.read(ROOT/'inputs/PUBLIC.json'):
        for family in ('user','global'):
            name=f'adaptive-{context["index"]:02}-{family}'
            data=prototype.data.model_copy(update={'name':name,'idx':context['index']*2+(family=='global'),
                'prompt':public_prompt(context,family),'context':context['text'],'answer':repr([gold[name]['answer']]),
                'source_id':14800000+2*context['index']+(family=='global'),'source_split':'leaf-train-named-history-excluded-adaptive',
                'context_window_id':1800+context['index'],'dataset':ROOT.name,
                'context_len':len(tokenizer.encode(context['text'],add_special_tokens=False).ids)})
            task=AdaptiveTask(data,prototype.config)
            task.public_records,task.plain_query,task.controller=context['records'],question(context,family),'free'
            tasks[name]=task
    return tasks


def with_prompt(task, arm):
    controller={'user_all':'all16','user_filter':'filter16','global_shared':'all16','user_free':'free','global_free':'free'}[arm]
    result=AdaptiveTask(task.data,task.config)
    result.public_records,result.plain_query,result.controller=task.public_records,task.plain_query,controller
    return result


def binding_for(policy):
    if policy!=c.read(old.ROOT/'SPEC.json')['policies']['step8']:
        raise ValueError('only prespecified historical step8 policy allowed')
    binding=prior.binding_for(policy)
    binding.pop('receipt_uptake_study',None)
    binding['adaptive_filter_study']=ROOT.name
    binding['decision_sha256']=c.file_hash(ROOT.parents[1]/'operations/2026-09-09-continuous-allocation/ADAPTIVE_FILTER_CPU_DECISION.md')
    return binding


def collector_source():
    source=prior.COLLECTOR.read_text()
    if hashlib.sha256(source.encode()).hexdigest()!=prior.COLLECTOR_SHA:raise ValueError('collector changed')
    for before,after in [('range(0, len(plan), 2)','range(0, len(plan), 5)'),
                         ('plan[offset : offset + 2]','plan[offset : offset + 5]'),
                         ('deadline = attempt["started_epoch"] + frozen["wall_time_cap_seconds"]',
                          'deadline = min(attempt["started_epoch"] + frozen["wall_time_cap_seconds"], frozen["collection_deadline_epoch"])')]:
        if source.count(before)!=1:raise ValueError('collector seam ambiguous')
        source=source.replace(before,after)
    return source


def collector():
    import ast
    import types
    module=types.ModuleType('adaptive_five_job_collector')
    module.__dict__.update(capture.base.__dict__)
    tree=ast.parse(collector_source())
    node=next(n for n in tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run')
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(prior.COLLECTOR),'exec'),module.__dict__)
    return module
