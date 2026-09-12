"""One-shot paired token-path audit. No model queries, polling or generated-code execution."""
import argparse
from collections import Counter
import contextlib
import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parent
STORE=ROOT.parents[1]
SIDE=STORE/'sidecars/openai-mrcr-procedural-sft-terminal-strip-disabled-v1'
OLD=STORE/'sidecars/openai-mrcr-procedural-sft-continue32-eval-v1/outputs/held-checkpoint32-001'
NEW=SIDE/'outputs/held-checkpoint32-001'
READY_SHA='686e484b6ffa0338b6b699537b10e4ea84f436a29d76baa0ec704f895a629d91'
PINS={}
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(path):PINS[str(path)]=sha(path);return json.loads(Path(path).read_text())
def write(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('x') as f:json.dump(value,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')

@functools.lru_cache(None)
def bindings():
    # Fresh CPU analyzer process; these are the sealed evaluation's exact import aliases.
    sys.path.insert(0,str(SIDE))
    import collect
    assert Path(collect.__file__).resolve()==SIDE/'collect.py'
    return collect

def path_projection(rows):
    return [{'status':r['status'],'model':r['model'],'sampling':r['sampling'],
        'prompt_ids':r.get('response',{}).get('tokens',{}).get('prompt_ids'),
        'completion_ids':r.get('response',{}).get('tokens',{}).get('completion_ids'),
        'completion_logprobs':r.get('response',{}).get('tokens',{}).get('completion_logprobs'),
        'parsed_content':r.get('response',{}).get('message',{}).get('content'),
        'tool_calls':[{k:t.get(k) for k in ('name','arguments','status')} for t in (r.get('response',{}).get('message',{}).get('tool_calls') or [])],
        'reasoning':r.get('response',{}).get('message',{}).get('reasoning_content')}
        for r in sorted(rows,key=lambda x:x['index'])]

def compare_paths(old,new):
    same_count=len(old)==len(new)
    fields=('status','model','sampling','prompt_ids','completion_ids','completion_logprobs','tool_calls','reasoning')
    same={k:same_count and all(a[k]==b[k] for a,b in zip(old,new)) for k in fields}
    strict=bool(old) and all(same[k] for k in fields if k!='completion_logprobs') and all(a['status']=='returned' for a in old)
    return {'same_call_count':same_count,'old_calls':len(old),'new_calls':len(new),
        'all_action_ids_equal':same['completion_ids'],'all_prompt_ids_equal':same['prompt_ids'],
        'all_model_sampling_equal':same['model'] and same['sampling'],'all_tool_calls_equal':same['tool_calls'],
        'all_logprobs_equal':same['completion_logprobs'],'strict_native_path_equal':strict,
        'fields_equal':same,'per_call':[{'position':i,'different_fields':[k for k in fields if a[k]!=b[k]],
            'parsed_content_equal':a['parsed_content']==b['parsed_content'],
            'old_action_sha256':digest(a['completion_ids']),'new_action_sha256':digest(b['completion_ids']),
            'old_prompt_sha256':digest(a['prompt_ids']),'new_prompt_sha256':digest(b['prompt_ids'])}
            for i,(a,b) in enumerate(zip(old,new))]}

def programs(trace):
    return [{'name':t.get('name'),'arguments':t.get('arguments')} for n in trace.get('nodes',[])
            for t in ((n.get('message') or {}).get('tool_calls') or []) if t.get('name')=='ipython']

def verify():
    ready=read(ROOT/'READY.json')
    assert ready['identity']==digest({k:v for k,v in ready.items() if k!='identity'})
    for path,want in ready['closure_sha256'].items():assert sha(path)==want,path
    assert sha(SIDE/'CPU_READY.json')==READY_SHA
    return ready

def stage(directory,patched):
    module=bindings();s=module.study
    result=read(directory/'science/RESULT.json') if (directory/'science/RESULT.json').exists() else None
    terminal=read(directory/'OWNER_TERMINAL.json') if (directory/'OWNER_TERMINAL.json').exists() else None
    if not terminal:return {'status':'PENDING_OWNER_TERMINAL','rows':{},'result':result}
    native=[read(p) for p in sorted((directory/'science/native-calls').glob('*-result.json'))]
    starts=[read(p) for p in sorted((directory/'science/native-calls').glob('*-start.json'))]
    binding=read(directory/'owned-service/BINDING.json') if (directory/'owned-service/BINDING.json').exists() else None
    expected=read(OLD/'owned-service/BINDING.json')
    if binding is not None:assert binding==expected,'fixed cp32 binding differs'
    if result:assert result['checkpoint_receipt_sha256']==read(SIDE/'CPU_READY.json')['checkpoint_receipt_sha256']
    if patched and result:
        contract=read(directory/'science/TERMINAL_STRIP_CONTRACT.json')
        assert contract==module.hooks.qualify()
    plan={x['id']:x for x in s.schedule('held')};gold=s.read(s.input_dir('held')/'HOST_GOLD.json')
    prefixes=s.read(s.input_dir('held')/'PREFIXES.json')
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    tokenizer=AutoTokenizer.from_pretrained(str(s.BASE),local_files_only=True);renderer=Qwen3Renderer(tokenizer)
    stops={renderer._im_end,renderer._endoftext};rows={}
    for p in sorted((directory/'science/episodes').glob('*.json')):
        item=read(p);c=item['coordinate'];assert c==plan[c['id']] and p.stem==c['id']
        raw=item['episode'];assert digest(raw)==item['episode_sha256'];assert len(raw['traces'])==1
        trace=raw['traces'][0];ours=module.source.inspect_trace(raw,gold[c['record_id']],native,prefixes[c['id']]['token_ids'])
        for key in ('raw_exact','scientifically_available','reward','native_mapping_complete'):
            assert ours[key]==item['derived'][key],key
        selected=sorted((r for r in native if r.get('session_id')==trace['id']),key=lambda r:r['index'])
        path=path_projection(selected);finals=[]
        for n in selected:
            if n['status']!='returned':continue
            payload=n['response'];ids=payload['tokens']['completion_ids']
            assert digest(ids)==n['evidence']['completion_ids_sha256']
            assert payload['usage']['prompt_tokens']==len(payload['tokens']['prompt_ids'])
            assert payload['usage']['completion_tokens']==len(ids)
            with module.hooks.installed() if patched else contextlib.nullcontext():parsed=renderer.parse_response(ids)
            assert (parsed.content or None)==payload['message']['content']
            if not parsed.tool_calls:
                stop=next((i for i,t in enumerate(ids) if t in stops),len(ids))
                before=ids[:stop];wire=tokenizer.decode(before,skip_special_tokens=False)
                bare=not parsed.reasoning_content and not any(t in tokenizer.all_special_ids for t in before)
                bare=bare and not any(x in wire for x in ('<think>','</think>','<tool_call>','</tool_call>','<tool_response>','</tool_response>'))
                finals.append({'wire':wire,'bare':bare,'native':payload['message']['content']})
        assert len(finals)<=1
        f=finals[0] if finals else None;answer=gold[c['record_id']]['answer'];reply=trace.get('root_reply')
        if f:assert (f['native'] or '')==(reply or '')
        category=('unavailable' if not ours['scientifically_available'] else 'returned_exact' if ours['raw_exact'] else
            'raw_exact_lost_at_boundary' if f and f['bare'] and f['wire']==answer else
            'model_edge_whitespace_difference' if f and f['bare'] and f['wire'].strip()==answer.strip() else
            'model_other_text_difference' if f and f['bare'] else 'model_invalid_or_no_bare_final')
        rows[c['id']]={'coordinate':c,'available':ours['scientifically_available'],'returned_exact':ours['raw_exact'],
            'official_score':ours['reward'],'category':category,'failure_class':ours['failure_class'],
            'path':path,'programs':programs(trace),'tool_observations':[n['message'].get('content') for n in trace['nodes'] if n.get('message',{}).get('role')=='tool'],
            'initial_prefix_exact':ours['initial_root_prefix_verified'],'root_final_sha256':digest(reply),
            'bare_raw_final_sha256':digest(f['wire']) if f and f['bare'] else None,
            'native_final_sha256':digest(f['native']) if f else None,'episode_sha256':sha(p)}
    returned=[r for r in native if r['status']=='returned']
    return {'status':'TERMINAL','rows':rows,'owner':terminal,'result':result,
        'physical':{'started':len(starts),'result_records':len(native),'returned':len(returned),
            'errors':sum(r['status']!='returned' for r in native),'start_only':len(starts)-len(native),
            'observed_prompt_tokens':sum(len(r['response']['tokens']['prompt_ids']) for r in returned),
            'observed_completion_tokens':sum(len(r['response']['tokens']['completion_ids']) for r in returned)},
        'categories':dict(Counter(r['category'] for r in rows.values())),
        'available':sum(r['available'] for r in rows.values()),'returned_exact':sum(r['available'] and r['returned_exact'] for r in rows.values())}

def build():
    old=stage(OLD,False);new=stage(NEW,True)
    if new['status']!='TERMINAL':return {'status':'PENDING','old_summary':{k:v for k,v in old.items() if k!='rows'},'new_status':new['status'],'polling':False}
    pairs=[]
    for c in bindings().study.schedule('held'):
        a=old['rows'].get(c['id']);b=new['rows'].get(c['id']);both=bool(a and b and a['available'] and b['available'])
        compared=compare_paths(a['path'],b['path']) if a and b else None
        same_programs=bool(a and b and a['programs']==b['programs']);same_obs=bool(a and b and a['tool_observations']==b['tool_observations'])
        win=both and b['returned_exact'] and not a['returned_exact'];loss=both and a['returned_exact'] and not b['returned_exact']
        clamp_only=bool(win and compared['strict_native_path_equal'] and same_programs and same_obs and a['category']=='raw_exact_lost_at_boundary')
        pairs.append({'coordinate':c,'paired_available':both,'win':win,'loss':loss,'strict_clamp_only_recovery':clamp_only,
            'programs_exact':same_programs,'observations_exact':same_obs,'path_comparison':compared,
            'old':{k:v for k,v in a.items() if k not in ('path','programs','tool_observations')} if a else None,
            'new':{k:v for k,v in b.items() if k not in ('path','programs','tool_observations')} if b else None,
            'old_path_sha256':digest(a['path']) if a else None,'new_path_sha256':digest(b['path']) if b else None})
    return {'status':'TERMINAL_PAIRED_RAW_AUDIT','planned_episodes_per_arm':32,'context_units':16,'repeats_per_context':2,
        'old':{k:v for k,v in old.items() if k!='rows'},'new':{k:v for k,v in new.items() if k!='rows'},'pairs':pairs,
        'paired_available':sum(p['paired_available'] for p in pairs),'wins':sum(p['win'] for p in pairs),'losses':sum(p['loss'] for p in pairs),
        'strict_clamp_only_recoveries':sum(p['strict_clamp_only_recovery'] for p in pairs),
        'strict_native_paths_equal':sum(bool(p['path_comparison'] and p['path_comparison']['strict_native_path_equal']) for p in pairs),
        'claim_limit':'Only matched all-action/prompt/model/sampling/program/observation paths attribute recovery to the terminal clamp; divergent trajectories remain descriptive. Research-exposed16contexts, not32independent units.',
        'source_sha256':dict(PINS),'source_READY_sha256':READY_SHA,'GPU_calls':0,'generated_programs_executed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','check']);p.add_argument('--output',type=Path);a=p.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';ready=verify()
    if a.command=='verify':print({'identity':ready['identity']})
    else:
        value=build();value['analyzer_READY_sha256']=sha(ROOT/'READY.json');value['created_epoch']=time.time()
        if a.output:write(a.output,value)
        print({k:v for k,v in value.items() if k in ('status','paired_available','wins','losses','strict_clamp_only_recoveries','strict_native_paths_equal')})
