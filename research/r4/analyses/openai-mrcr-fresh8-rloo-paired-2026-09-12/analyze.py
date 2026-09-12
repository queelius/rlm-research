"""Thin explicit bindings over the reviewed source-to-raw paired scorer."""
import argparse
from collections import Counter
import functools
import importlib.util
import os
from pathlib import Path
import sys
import time
import types

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
SIDE=STORE/'sidecars/openai-mrcr-cp32-fresh8-final-rloo-eval-v1'
SOURCE_READY_SHA='5bb409be9a59601772527b052c28d445809b3e0eeb3d40ea6d33a2684de0028c'
CORE=ROOT.parent/'openai-mrcr-fixed-baseline-rl-paired-2026-09-12/analyze.py'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
core=load('freshRLOO_reviewed_raw_scorer',CORE)
sha=core.sha;read=core.read;write=core.write;digest=core.digest;pair=core.pair;PINS=core.PINS

@functools.lru_cache(None)
def bindings():
    names=('study','checkpoint','collect');old={n:sys.modules.get(n) for n in names};paths=list(sys.path)
    try:
        for n in names:sys.modules.pop(n,None)
        sys.path.insert(0,str(SIDE));c=load('freshRLOO_native_evaluation_collector',SIDE/'collect.py')
    finally:
        sys.path[:]=paths
        for n,v in old.items():
            if v is None:sys.modules.pop(n,None)
            else:sys.modules[n]=v
    assert c.study.ROOT==SIDE and c.source.study is c.study and c.source.checkpoint is c.checkpoint
    return c
core.bindings=bindings

def stage(phase,arm):
    c=bindings();s=c.study
    assert phase in s.CAPS and arm in ('cp32','fixed_baseline_RL','updated')
    if arm=='updated':
        directory=SIDE/f'outputs/{phase}-001'
        expected=read(s.train.OUTPUT/'checkpoint-0001/EVAL_BINDING.json')
    else:
        directory=s.CONTROLS[phase][arm]
        expected=read(s.TRAINING/'PARENT_BINDING.json') if arm=='cp32' else read(s.prior.TRAINING/'outputs/attempt-001/checkpoint-0001/EVAL_BINDING.json')
    actual=directory/'owned-service/BINDING.json'
    if actual.exists():assert read(actual)==expected
    facade=types.SimpleNamespace(**vars(s));facade.BASELINES={**s.BASELINES,phase:directory}
    collector=types.SimpleNamespace(**vars(c));collector.study=facade
    globals_map={**core.stage.__globals__,'SIDE':SIDE,'bindings':lambda:collector}
    result=types.FunctionType(core.stage.__code__,globals_map)(phase,'updated' if arm=='updated' else 'cp32')
    result.update(arm=arm,explicit_expected_binding_sha256=digest(expected),
                  expected_root_alias=expected['role_map']['root'],stop_counts=dict(Counter(r['stop'] for r in result['rows'].values())))
    return result

def verify():
    r=read(ROOT/'CPU_READY.json');assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    assert sha(SIDE/'READY.json')==SOURCE_READY_SHA
    return r

def build():
    c=bindings();s=c.study
    pending=[p for p in s.CAPS if not (SIDE/f'outputs/{p}-001/OWNER_TERMINAL.json').exists()]
    if pending:return dict(status='PENDING_OWNER_TERMINALS',pending=pending,GPU_calls=0,polling=False)
    q=c.checkpoint.verify_checkpoint();phases={}
    for phase in s.CAPS:
        arms={name:stage(phase,name) for name in (*s.CONTROLS[phase],'updated')}
        comparisons={name:pair(s.schedule(phase),arms[name]['rows'],arms['updated']['rows']) for name in s.CONTROLS[phase]}
        phases[phase]=dict(arms=arms,comparisons=comparisons)
    full=all(arm['qualified'] for x in phases.values() for arm in x['arms'].values())
    return dict(status='COMPLETE_PAIRED_AUDIT' if full else 'TERMINAL_PARTIAL_OR_INTEGRITY_HOLD',
        phases=phases,planned_new_outputs=64,primary='held:RLOO_vs_cp32',
        secondary_short='held:RLOO_vs_fixed_baseline_RL',context_units={'held':16,'long':16,'fourneedle':16},
        checkpoint_qualification=q,training=read(s.train.OUTPUT/'RESULT.json'),
        training_owner=read(s.train.OUTPUT/'OWNER_TERMINAL.json'),source_sha256=dict(PINS),
        source_READY_sha256=SOURCE_READY_SHA,GPU_calls=0,generated_programs_executed=False,
        interpretation='Different weights: native token equality is descriptive, not clamp-only causality. Short uses the new decoding-replica seeds for every arm. Batch and reward estimator both differ between RL recipes. All panels are research-exposed; base pretraining unknown. Repeats are clustered within sixteen contexts per panel. Mapping, stop/failure rules and clean-observation taxonomy reuse the reviewed collector; scores, native token decoding and costs are recomputed.')

def markdown(r):
    if r['status'].startswith('PENDING'):return '# Fresh8 RLOO paired audit\n\nPending: '+', '.join(r['pending'])+'. One check only.\n'
    out=['# Fresh8 RLOO paired native readout','',r['status'],'']
    for phase,x in r['phases'].items():
        for name,arm in x['arms'].items():
            p=arm['physical']
            out.append(f"{phase} {name}: {arm['correct']}/{arm['planned']} correct; {arm['available']} available, {arm['unavailable']} unavailable. Physical {p['returned']} returned/{p['error_results']} errors/{p['start_only']} start-only/{p['orphan_returned']} orphan returns; {p['prompt_tokens']} input + {p['completion_tokens']} output tokens; {p['unknown_usage_calls']} unknown-cost calls; owner {arm['owner']['elapsed_seconds']:.2f}s.")
            out.append(f"Copy/retrieval taxonomy: {arm['mechanism_counts']}; stops {arm['stop_counts']}.")
        for control,p in x['comparisons'].items():
            out.append(f"RLOO vs {control}: {p['wins']} wins/{p['losses']} losses in {p['paired_available']} available pairs; {p['unknown_pairs']} unknown. Contexts improved/worsened {p['contexts_with_positive_paired_delta']}/{p['contexts_with_negative_paired_delta']}, {p['complete_context_pairs']}/{p['context_units']} complete.")
        out.append('')
    out.extend([f"Training separate: {r['training']['elapsed_seconds']:.2f}s science, {r['training_owner']['elapsed_seconds']:.2f}s owner.",'',r['interpretation']])
    return '\n'.join(out)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','check']);p.add_argument('--output',type=Path);a=p.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';ready=verify()
    if a.command=='verify':print(ready['identity'])
    else:
        r=build();r['analyzer_READY_sha256']=sha(ROOT/'CPU_READY.json');r['created_epoch']=time.time()
        if a.output:write(a.output,r);write(a.output.with_suffix('.md'),markdown(r))
        print({'status':r['status'],'pending':r.get('pending')})
