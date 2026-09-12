"""One-shot in-sample32 audit reusing the reviewed native decoder and causal scorer."""
import argparse
from collections import Counter
import functools
import importlib.util
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
SIDE=STORE/'sidecars/openai-mrcr-cp32-fresh8-final-rloo-train-readout-v1'
SOURCE_SHA='8f035e96a8bcf26a1a4a7219aabfdd0f9ed2fab2f0fe965a8f5426c02ca41827'
CORE=ROOT.parent/'openai-mrcr-fixed-baseline-rl-paired-2026-09-12/analyze.py'
spec=importlib.util.spec_from_file_location('fresh8_trainread_raw_core',CORE)
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
sha=core.sha;read=core.read;write=core.write;digest=core.digest

@functools.lru_cache(None)
def bindings():
    names=('study','checkpoint','collect');saved={n:sys.modules.get(n) for n in names};paths=list(sys.path)
    try:
        for n in names:sys.modules.pop(n,None)
        sys.path.insert(0,str(SIDE));spec=importlib.util.spec_from_file_location('fresh8_trainread_native',SIDE/'collect.py')
        c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    finally:
        sys.path[:]=paths
        for n,v in saved.items():
            if v is None:sys.modules.pop(n,None)
            else:sys.modules[n]=v
    assert c.study.ROOT==SIDE and c.source.study is c.study and c.source.checkpoint is c.checkpoint
    return c
core.bindings=bindings;core.SIDE=SIDE

def stage(arm):
    s=bindings().study;assert arm in ('cp32','updated')
    directory=s.BASELINE if arm=='cp32' else SIDE/'outputs/train-001'
    expected=read(s.TRAINING/'PARENT_BINDING.json') if arm=='cp32' else bindings().checkpoint.binding('updated')
    if (directory/'owned-service/BINDING.json').exists():assert read(directory/'owned-service/BINDING.json')==expected
    result=core.stage('train',arm)
    result['expected_binding_sha256']=digest(expected)
    result['stop_counts']=dict(Counter(r['stop'] for r in result['rows'].values()))
    return result

def grouped(plan,left,right):
    groups={}
    for c in plan:groups.setdefault(c['record_id'],[]).append(c)
    result=[]
    def bit(row):return str(int(row['raw_exact'])) if row and row['available'] else 'U'
    for ident,rows in groups.items():
        rows=sorted(rows,key=lambda c:c['repeat']);a=[left.get(c['id']) for c in rows];b=[right.get(c['id']) for c in rows]
        av=''.join(map(bit,a));bv=''.join(map(bit,b))
        result.append(dict(record_id=ident,old_G4=av,new_G4=bv,complete='U' not in av+bv,
            paired_net_correct=sum(int(y['raw_exact'])-int(x['raw_exact']) for x,y in zip(a,b) if x and y and x['available'] and y['available'])))
    return result

def boundary(row):
    if row is None:return None
    item=read(row['episode_path']);assert digest(item['episode'])==item['episode_sha256']
    traces=item['episode'].get('traces') or [];reply=traces[0].get('root_reply') if len(traces)==1 else None
    gold=item['derived']['answer'];text=reply if isinstance(reply,str) else ''
    return dict(copy_type=row['copy_type'],actual_final_text=row['actual_final_text'],stop=row['stop'],
        clean_target_observed=row['mechanism']['clean_target_observed'],final_characters=len(text),
        missing_only_two_spaces=text+'  '==gold,extra_only_newlines=text!=gold and text.rstrip('\n')==gold,
        final_sha256=row['final_sha256'])

def build():
    terminal=SIDE/'outputs/train-001/OWNER_TERMINAL.json'
    if not terminal.exists():return dict(status='PENDING_OWNER_TERMINAL',polling=False,GPU_calls=0)
    c=bindings();s=c.study;q=c.checkpoint.verify_checkpoint();a=stage('cp32');b=stage('updated')
    p=core.pair(s.schedule('train'),a['rows'],b['rows']);changed=[]
    for pair in p['pairs']:
        if pair['native_token_paths_equal_descriptive_only']:continue
        ident=pair['coordinate']['id'];x=a['rows'].get(ident);y=b['rows'].get(ident)
        xa=x['native_actions'] if x else [];ya=y['native_actions'] if y else []
        changed.append(dict(pair=pair,old=boundary(x),new=boundary(y),
            first_action_identical=bool(xa and ya and xa[0]['action_sha256']==ya[0]['action_sha256']),
            first_prompt_identical=bool(xa and ya and xa[0]['prompt_sha256']==ya[0]['prompt_sha256'])))
    groups=grouped(s.schedule('train'),a['rows'],b['rows'])
    return dict(status='COMPLETE_PAIRED_AUDIT' if a['qualified'] and b['qualified'] else 'TERMINAL_PARTIAL_OR_INTEGRITY_HOLD',
        planned_per_arm=32,context_units=8,cp32=a,updated=b,pairing=p,groups=groups,changed_paths=changed,
        full_native_paths_identical=sum(x['native_token_paths_equal_descriptive_only'] for x in p['pairs']),
        checkpoint_qualification=q,training_result=read(s.train.OUTPUT/'RESULT.json'),
        training_owner=read(s.train.OUTPUT/'OWNER_TERMINAL.json'),source_sha256=dict(core.PINS),
        source_READY_sha256=SOURCE_SHA,GPU_calls=0,generated_programs_executed=False,
        interpretation='Original optimized training batch and same decoding seeds: in-sample diagnostic, not transfer or independent replication. All32 retained, including20 zero-advantage trajectories. Native token decoding, official scores and costs recomputed; causal/clean-observation taxonomy reuses reviewed helpers. Eight context clusters, not32 independent tasks. Changed weights prevent clamp-only causal attribution; no automatic optimizer admission.')

def markdown(r):
    if r['status'].startswith('PENDING'):return '# Fresh8 RLOO training readout\n\nPending; one check only, no polling.\n'
    a=r['cp32'];b=r['updated'];p=r['pairing']
    out=['# Fresh8 RLOO: in-sample behavioral diagnostic','',r['status'],'',
        f"Exact: cp32 {a['correct']}/32 → RLOO {b['correct']}/32; available {a['available']}/{b['available']}; unavailable {a['unavailable']}/{b['unavailable']}. {p['wins']} wins/{p['losses']} losses, {p['unknown_pairs']} unknown pairs. {r['full_native_paths_identical']}/32 identical native paths.",'',
        '| Context | cp32 G4 | RLOO G4 | Paired net |','|---|---|---|---|']
    for g in r['groups']:out.append(f"| {g['record_id']} | {g['old_G4']} | {g['new_G4']} | {g['paired_net_correct']} |")
    out+=['','U denotes unavailable/unattempted, never incorrect.']
    for name,v in [('cp32',a),('RLOO',b)]:
        x=v['physical'];out += ['',f"{name}: copy types {v['copy_types']}; stops {v['stop_counts']}.",
            f"Physical: {x['returned']} returns, {x['error_results']} errors, {x['start_only']} start-only, {x['orphan_returned']} orphan returns; {x['prompt_tokens']} input + {x['completion_tokens']} output tokens, {x['unknown_usage_calls']} unknown-cost calls; owner {v['owner']['elapsed_seconds']:.2f}s."]
    out+=['',f"Changed paths: {len(r['changed_paths'])}; full per-pair copying/action/observation fields in JSON, without answer text.",
          f"Training separate: {r['training_result']['elapsed_seconds']:.2f}s science / {r['training_owner']['elapsed_seconds']:.2f}s owner.",'',r['interpretation']]
    return '\n'.join(out)+'\n'

def verify():
    r=read(ROOT/'CPU_READY.json');assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    assert sha(SIDE/'READY.json')==SOURCE_SHA;return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','check']);p.add_argument('--output',type=Path);args=p.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';ready=verify()
    if args.command=='verify':print(ready['identity'])
    else:
        r=build();r['analyzer_READY_sha256']=sha(ROOT/'CPU_READY.json')
        if args.output:write(args.output,r);write(args.output.with_suffix('.md'),markdown(r))
        print({'status':r['status']})
