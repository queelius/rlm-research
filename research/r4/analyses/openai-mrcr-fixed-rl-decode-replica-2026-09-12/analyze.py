"""Rebind the reviewed paired native audit to both freshly generated replica arms."""
import argparse
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
SIDE=STORE/'sidecars/openai-mrcr-cp32-fixed-baseline-final-rl-decode-replica-v1'
PRIOR=STORE/'analyses/openai-mrcr-fixed-baseline-rl-paired-2026-09-12'

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def attempt(arm):
    if arm not in ('cp32','updated'):raise ValueError('only the fixed new replica arms')
    return SIDE/f'outputs/{arm}-001'

def bind():
    spec=importlib.util.spec_from_file_location('reviewed_fixed_rl_native_audit',PRIOR/'analyze.py')
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    sys.path.insert(0,str(SIDE))
    import collect
    assert Path(collect.__file__).resolve()==SIDE/'collect.py'
    s=collect.study
    facade=SimpleNamespace(BASE=s.BASE,BASELINES={'held':attempt('cp32')},
        schedule=lambda phase:s.schedule('cp32'),input_dir=lambda phase:s.input_dir('cp32'),
        read=s.read,train=s.prior.train)
    a.bindings=lambda:SimpleNamespace(study=facade,checkpoint=collect.checkpoint,
        source=collect.source,hooks=collect.hooks)
    # One explicit directory projection; score, token decode, mapping and costs stay identical.
    old="directory=s.BASELINES[phase] if arm=='cp32' else SIDE/f'outputs/{phase}-001'"
    text=inspect.getsource(a.stage);assert text.count(old)==1
    a.replica_attempt=attempt
    exec(compile(text.replace(old,'directory=replica_attempt(arm)'),str(PRIOR/'analyze.py')+':new-replica-directories','exec'),a.__dict__)
    return a,s

def verify():
    assert sha(SIDE/'READY.json')=='25d86737b647d1e78815b3b45f6127ff454fad0ba2803acc5a2e5181b967e971'
    assert sha(PRIOR/'READY.json')=='865df0f472c50d5817c65a0f90cfde44ffe7066a0b48cbfbd32d529b813cee23'
    for path in (SIDE/'READY.json',PRIOR/'READY.json'):
        receipt=json.loads(path.read_text())
        for name,want in receipt['closure_sha256'].items():assert sha(name)==want,name
    a,s=bind();s.verify();return a,s

def build():
    a,s=verify()
    if not all((attempt(arm)/'OWNER_TERMINAL.json').exists() for arm in ('cp32','updated')):
        return dict(status='PENDING_TWO_REPLICA_TERMINALS',GPU_calls=0,polling=False)
    a.bindings().checkpoint.verify_checkpoint()
    old=a.stage('held','cp32');new=a.stage('held','updated')
    pairing=a.pair(s.schedule('cp32'),old['rows'],new['rows'])
    return dict(status='COMPLETE_PAIRED_AUDIT' if old['qualified'] and new['qualified'] else 'TERMINAL_PARTIAL_OR_INTEGRITY_HOLD',
        phases={'held':dict(cp32=old,updated=new,pairing=pairing)},
        context_units=16,episodes_per_arm=32,old_controls_reused=False,new_training=False,
        training=a.read(s.prior.train.OUTPUT/'RESULT.json'),training_owner=a.read(s.prior.train.OUTPUT/'OWNER_TERMINAL.json'),
        source_sha256=dict(a.PINS),replica_READY_sha256=sha(SIDE/'READY.json'),
        analyzer_sha256=sha(__file__),original_analyzer_READY_sha256=sha(PRIOR/'READY.json'),GPU_calls=0,
        interpretation='Two fresh decoding seeds on the same16 exposed contexts, both fixed models newly evaluated. No new training or independent dataset; repeated seeds are not independent contexts. Saved earlier training cost is context, not newly spent compute.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['check']);args=parser.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    result=build()
    if result['status'].startswith('PENDING'):print(result)
    else:
        a,_=bind();a.write(ROOT/'RESULTS.json',result)
        a.write(ROOT/'REPORT.md',a.markdown(result))
        p=result['phases']['held']
        print(dict(status=result['status'],cp32=p['cp32']['correct'],updated=p['updated']['correct'],wins=p['pairing']['wins'],losses=p['pairing']['losses']))
