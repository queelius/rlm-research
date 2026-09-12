"""Fixed three-arm/two-panel native audit; no model calls, polling or generated-code execution."""
import argparse
from collections import Counter
import functools
import importlib.util
import os
from pathlib import Path
import sys
import types

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
SIDE=STORE/'sidecars/openai-mrcr-cp32-fresh8-final-rloo-lr1e4-eval-v1'
SOURCE_SHA='9373367ef6c6f7441d5415a4f852ce86b42c0e0e8d101ab75dd983c1172fc193'
PRIOR=ROOT.parent/'openai-mrcr-fresh8-rloo-training-readout-2026-09-12/analyze.py'
PATHS=ROOT.parent/'openai-mrcr-fresh8-rloo-paired-2026-09-12/audit_changes.py'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
prior=load('dose10_reviewed_train_audit',PRIOR);core=prior.core
sha=core.sha;read=core.read;write=core.write;digest=core.digest
saved=sys.modules.get('analyze');sys.modules['analyze']=types.SimpleNamespace(core=core,read=read,sha=sha,digest=digest)
try:paths=load('dose10_reviewed_inert_paths',PATHS)
finally:
    if saved is None:sys.modules.pop('analyze',None)
    else:sys.modules['analyze']=saved

@functools.lru_cache(None)
def bindings():
    names=('study','checkpoint','collect');saved={n:sys.modules.get(n) for n in names};oldpath=list(sys.path)
    try:
        for n in names:sys.modules.pop(n,None)
        sys.path.insert(0,str(SIDE));c=load('dose10_qualified_native_collector',SIDE/'collect.py')
    finally:
        sys.path[:]=oldpath
        for n,v in saved.items():
            if v is None:sys.modules.pop(n,None)
            else:sys.modules[n]=v
    assert c.study.ROOT==SIDE and c.source.study is c.study and c.source.checkpoint is c.checkpoint
    return c
core.bindings=bindings;core.SIDE=SIDE

def stage(phase,arm):
    c=bindings();s=c.study;assert phase in s.CAPS and arm in ('cp32','LR1e5','LR1e4')
    directory=SIDE/f'outputs/{phase}-001' if arm=='LR1e4' else s.CONTROLS[phase][arm]
    expected=(c.checkpoint.binding('updated') if arm=='LR1e4' else
              read(s.TRAINING/'PARENT_BINDING.json') if arm=='cp32' else
              read(s.prior.train.OUTPUT/'checkpoint-0001/EVAL_BINDING.json'))
    if (directory/'owned-service/BINDING.json').exists():assert read(directory/'owned-service/BINDING.json')==expected
    facade=types.SimpleNamespace(**vars(s));facade.BASELINES={**s.BASELINES,phase:directory}
    collector=types.SimpleNamespace(**vars(c));collector.study=facade
    scoped={**core.stage.__globals__,'SIDE':SIDE,'bindings':lambda:collector}
    result=types.FunctionType(core.stage.__code__,scoped)(phase,'updated' if arm=='LR1e4' else 'cp32')
    result.update(arm=arm,expected_binding_sha256=digest(expected),
                  stop_counts=dict(Counter(r['stop'] for r in result['rows'].values())))
    return result

def detail(row):
    if row is None:return None
    final=prior.boundary(row)
    if not row['available']:return dict(final=final,unavailable=True,raw_path=row['episode_path'])
    item,trace,native=paths.load_episode(row)
    obs=[n['message']['content'] for n in trace.get('nodes',[]) if n.get('message',{}).get('role')=='tool']
    return dict(final=final,programs=paths.programs(trace),native=[paths.action(n) for n in native],
        observation_characters=sum(len(v) for v in obs),observation_hashes=[digest(v) for v in obs],
        raw_path=row['episode_path'],raw_sha256=row['episode_file_sha256'])

def comparison(plan,left,right):
    result=core.pair(plan,left,right);changed=[]
    for pair in result['pairs']:
        if pair['native_token_paths_equal_descriptive_only']:continue
        ident=pair['coordinate']['id'];a=left.get(ident);b=right.get(ident)
        x=a['native_actions'] if a else [];y=b['native_actions'] if b else []
        changed.append(dict(pair=pair,old=detail(a),new=detail(b),
            first_action_identical=bool(x and y and x[0]['action_sha256']==y[0]['action_sha256']),
            first_prompt_identical=bool(x and y and x[0]['prompt_sha256']==y[0]['prompt_sha256'])))
    result['changed_paths']=changed
    result['native_paths_identical']=sum(x['native_token_paths_equal_descriptive_only'] for x in result['pairs'])
    result['boundary_only_wins']=sum(x['pair']['win'] and x['pair']['programs_equal'] and x['pair']['observations_equal']
        and x['old']['final']['copy_type']=='edge_whitespace_difference' and x['new']['final']['copy_type']=='exact' for x in changed)
    return result

def vectors(plan,arms):
    groups={}
    for c in plan:groups.setdefault(c['record_id'],[]).append(c)
    result=[]
    for ident,coords in groups.items():
        coords=sorted(coords,key=lambda c:c['repeat']);values={}
        for arm,data in arms.items():
            rows=[data['rows'].get(c['id']) for c in coords]
            values[arm]=''.join(str(int(r['raw_exact'])) if r and r['available'] else 'U' for r in rows)
        result.append(dict(record_id=ident,vectors=values,planned_repeats=len(coords)))
    return result

def build():
    c=bindings();s=c.study;pending=[p for p in s.CAPS if not (SIDE/f'outputs/{p}-001/OWNER_TERMINAL.json').exists()]
    if pending:return dict(status='PENDING_OWNER_TERMINALS',pending=pending,polling=False,GPU_calls=0)
    q=c.checkpoint.verify_checkpoint();phases={}
    for phase in s.CAPS:
        arms={arm:stage(phase,arm) for arm in ('cp32','LR1e5','LR1e4')};plan=s.schedule(phase)
        paired={arm:comparison(plan,arms[arm]['rows'],arms['LR1e4']['rows']) for arm in ('cp32','LR1e5')}
        phases[phase]=dict(arms=arms,comparisons=paired,context_vectors=vectors(plan,arms))
    full=all(a['qualified'] for p in phases.values() for a in p['arms'].values())
    return dict(status='COMPLETE_PAIRED_AUDIT' if full else 'TERMINAL_PARTIAL_OR_INTEGRITY_HOLD',phases=phases,
        new_planned_outputs=64,context_units={'train':8,'held':16},checkpoint_qualification=q,
        training={arm:dict(result=read(root/'RESULT.json'),owner=read(root/'OWNER_TERMINAL.json')) for arm,root in
                  [('LR1e5',s.prior.train.OUTPUT),('LR1e4',s.train.OUTPUT)]},
        source_sha256=dict(core.PINS),source_READY_sha256=SOURCE_SHA,GPU_calls=0,optimizer_steps=0,
        generated_programs_executed=False,
        interpretation='Same original cp32 and frozen native batch, nominal LR-only one-step recipe contrast; backward arithmetic is not bitwise identical. Training is in-sample; held16x2 is research-exposed development evidence. Eight training and16 held context clusters, not independent repeats. Official scores/native decode/cost are recomputed; causal/clean-observation definitions reuse reviewed helpers. No further optimizer, threshold tuning or best-arm selection follows automatically.')

def markdown(r):
    if r['status'].startswith('PENDING'):return '# Fixed two-dose readout\n\nPending: '+', '.join(r['pending'])+'. No polling.\n'
    out=['# One-step dose: local fit versus exposed held transfer','',r['status'],'']
    for phase,x in r['phases'].items():
        out+=['## '+phase,'','| Arm | Correct/32 | Available | Clean target | Input/output tokens | Returned/errors/start-only |','|---|---|---|---|---|---|']
        for name,a in x['arms'].items():
            p=a['physical'];clean=sum(v['available'] and v['mechanism']['clean_target_observed'] for v in a['rows'].values())
            out.append(f"| {name} | {a['correct']}/32 | {a['available']} | {clean} | {p['prompt_tokens']}/{p['completion_tokens']} | {p['returned']}/{p['error_results']}/{p['start_only']} |")
        out+=['']
        for name,p in x['comparisons'].items():
            out.append(f"LR1e-4 vs {name}: {p['wins']} wins/{p['losses']} losses, {p['unknown_pairs']} unknown pairs; {p['native_paths_identical']}/32 identical native paths; {p['boundary_only_wins']} wins preserve programs/observations and repair only edge whitespace. Contexts improved/worsened {p['contexts_with_positive_paired_delta']}/{p['contexts_with_negative_paired_delta']}.")
        out+=['','| Context | cp32 | LR1e-5 | LR1e-4 |','|---|---|---|---|']
        for v in x['context_vectors']:out.append('| '+v['record_id']+' | '+' | '.join(v['vectors'][n] for n in ('cp32','LR1e5','LR1e4'))+' |')
        out+=['','U is unavailable, not wrong. All changed paths include actual token tails, parsed program hashes/literal slots, observation hashes/volume and terminal-copy flags in JSON; answers are not copied here.','']
    out+=['Training/owner timings and physical versus mapped policy costs are separate in JSON. Errors/start-only costs are unknown, not zero. Prior controls are reused, not newly charged for each comparison.','',r['interpretation']]
    return '\n'.join(out)+'\n'

def verify():
    r=read(ROOT/'CPU_READY.json');assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    assert sha(SIDE/'READY.json')==SOURCE_SHA;return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','check']);p.add_argument('--output',type=Path);a=p.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';ready=verify()
    if a.command=='verify':print(ready['identity'])
    else:
        r=build();r['analyzer_READY_sha256']=sha(ROOT/'CPU_READY.json')
        if a.output:write(a.output,r);write(a.output.with_suffix('.md'),markdown(r))
        print({'status':r['status']})
