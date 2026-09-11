"""Private episode overlay and native dispatch accounting; no host model code."""
import ast
import asyncio
import contextvars
import hashlib
import importlib.util
import json
import sys
import time
import types
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
ARMS=('control','child_role_suffix')
SUFFIX=('For this child task, classify the answer type requested by each supplied question; '
        'do not answer the embedded questions. Work from the supplied text, without Python, '
        'package installation or external sources. Return only the requested labels in the requested format.')
COORDINATE=contextvars.ContextVar('child_role_suffix_coordinate',default=None)
PINS={
    SIDE/'root-only-credit-v1/capture.py':'b4fe35621c066c69638a85f15c36920490646f379ede491549806ec0fa4d0675',
    SIDE/'root-only-credit-v1/native_routing.py':'5ea35866be87662372ca1b312ddabbbab9ce009915fbfaa31353455ec702e841',
    SIDE/'leaf-role-routing-v1/source/routing.py':'8575081694a6ceea8d5f4058d4f625eb81d34f617a680f94bc06968e3a3ca78f',
    SIDE/'plan-hint-crossover-v1/driver.py':'406a64ca59e4d77e6126c3fd97339c57cb5d7aef6808c998d7e18be7e6456832',
}


def read(path): return json.loads(Path(path).read_text())
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def file_hash(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


def checked_import(name,path,sha):
    if file_hash(path)!=sha: raise ValueError('source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


role=checked_import('suffix_original_role',SIDE/'leaf-role-routing-v1/source/routing.py',PINS[SIDE/'leaf-role-routing-v1/source/routing.py'])
write_once=role.write_once


def patch_engine(source,arm):
    if arm not in ARMS: raise ValueError('unknown arm')
    patched=role.patch_engine(source)
    if arm=='control': return patched
    before='            system_prompt = self._load_system_prompt(self._active_tools)\n'
    if patched.count(before)!=1: raise ValueError('system construction seam changed')
    after=before+'            if self.runtime_config.invocation.depth == 1:\n                system_prompt += '+repr('\n\n'+SUFFIX)+'\n'
    return patched.replace(before,after)


def overlay_for_coordinate():
    row=COORDINATE.get()
    if row is None or row['arm'] not in ARMS: raise ValueError('trusted coordinate absent during setup')
    function=types.FunctionType(role.overlay_program.__code__,
        {**role.overlay_program.__globals__,'patch_engine':lambda source:patch_engine(source,row['arm'])})
    return function()


async def run_coordinate(row,run_slot):
    if row['arm'] not in ARMS: raise ValueError('unknown coordinate arm')
    token=COORDINATE.set(dict(row))
    try: return await run_slot()
    finally: COORDINATE.reset(token)


class DispatchPrevented(RuntimeError): pass


class DispatchBudget:
    def __init__(self,output,limit=2048):
        self.output,self.limit=Path(output),limit
        self.sent,self.prevented=0,0
        self.exhausted=asyncio.Event()

    def before_dispatch(self,record):
        allowed=self.sent<self.limit
        if allowed: self.sent+=1
        else:
            self.prevented+=1
            self.exhausted.set()
        record['dispatch_attempted']=allowed
        record['dispatch_prevented']=not allowed
        write_once(self.output/f'{self.sent+self.prevented:06d}.json',{
            'request_id':record.get('request_id'),'session_id':record.get('session_id'),
            'invocation':record.get('invocation'),'depth':record.get('depth'),
            'actual_alias':record.get('actual_alias'),'dispatch_attempted':allowed,
            'sampled_completion':None,'sent_so_far':self.sent,'prevented_so_far':self.prevented,
            'epoch':time.time(),'boundary':'last native request hook, before HTTP transport',
            'wire_request':record.get('native_wire_request')})
        if not allowed: raise DispatchPrevented('study native dispatch ceiling; not a provider/sample failure')


def native_hooks(guard):
    path=SIDE/'root-only-credit-v1/native_routing.py'
    if file_hash(path)!=PINS[path]: raise ValueError('native source changed')
    source=path.read_text()
    changes=[
        ('role.overlay_program()','overlay_for_coordinate()'),
        ('{"runtime": runtime.name, "exit_code": result.exit_code,',
         '{"runtime": runtime.name, "coordinate": COORDINATE.get(), "exit_code": result.exit_code,'),
        ('record["native_wire_request"] = {"url": str(request.url), "body": body}',
         'record["native_wire_request"] = {"url": str(request.url), "body": body}\n        guard.before_dispatch(record)'),
    ]
    for before,after in changes:
        if source.count(before)!=1: raise ValueError('native hook seam changed: '+before)
        source=source.replace(before,after)
    module=types.ModuleType('suffix_private_native_hooks')
    module.__file__=str(path)
    module.__dict__.update(overlay_for_coordinate=overlay_for_coordinate,COORDINATE=COORDINATE,guard=guard)
    exec(compile(source,str(path),'exec'),module.__dict__)
    module.executed_source_sha256=hashlib.sha256(source.encode()).hexdigest()
    return module


def collector(base):
    path=SIDE/'plan-hint-crossover-v1/driver.py'
    if file_hash(path)!=PINS[path]: raise ValueError('collector changed')
    source=path.read_text()
    before='episode = await environment.run_slot(RunSlot(task), q.make_context(endpoint, row))'
    if source.count(before)!=1: raise ValueError('collector arm seam changed')
    source=source.replace(before,'episode = await run_coordinate(row, lambda: environment.run_slot(RunSlot(task), q.make_context(endpoint, row)))')
    module=types.ModuleType('suffix_private_collector')
    module.__dict__.update(base.__dict__)
    module.run_coordinate=run_coordinate
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run')
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),module.__dict__)
    module.executed_source_sha256=hashlib.sha256(source.encode()).hexdigest()
    return module


def outcome_state(raw,censored,recovered_error):
    observable=raw.get('ok') is True and not censored
    return {'observable_reward':raw.get('reward') if observable else None,
        'empty_final':raw.get('answer') in ('',None),'budget_censored':bool(censored),
        'recovered_provider_error':bool(recovered_error and observable),
        'episode_infrastructure_or_incomplete':not observable and not censored,
        'answer_preserved':raw.get('answer')}
