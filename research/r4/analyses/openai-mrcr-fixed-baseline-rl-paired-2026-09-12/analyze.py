"""One-shot paired source-to-raw audit; no model calls or generated code execution."""
import argparse
from collections import Counter
import functools
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
SIDE=STORE/'sidecars/openai-mrcr-cp32-fixed-baseline-final-rl-eval-v1'
SOURCE_READY_SHA='c7de2ad71a4b0a6774dfd7b077193e82cf5f68d5857665f30f2c0bdf87847e0b'
HELPER=STORE/'analyses/openai-mrcr-long-transfer-independent-2026-09-12/analyze.py'
PINS={}
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(p):PINS[str(p)]=sha(p);return json.loads(Path(p).read_text())
def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:
        if isinstance(x,str):f.write(x)
        else:json.dump(x,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
@functools.lru_cache(None)
def bindings():
    sys.path.insert(0,str(SIDE));import collect
    assert Path(collect.__file__).resolve()==SIDE/'collect.py'
    return collect
@functools.lru_cache(None)
def helper():
    spec=importlib.util.spec_from_file_location('fixedRL_paired_official_mechanism',HELPER)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
@functools.lru_cache(None)
def renderer():
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    tok=AutoTokenizer.from_pretrained(str(bindings().study.BASE),local_files_only=True)
    return tok,Qwen3Renderer(tok),len(tok)

def verify():
    r=read(ROOT/'READY.json');assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    assert sha(SIDE/'READY.json')==SOURCE_READY_SHA
    return r

def stage(phase,arm):
    c=bindings();s=c.study
    directory=s.BASELINES[phase] if arm=='cp32' else SIDE/f'outputs/{phase}-001'
    terminal=read(directory/'OWNER_TERMINAL.json')
    rp=directory/'science/RESULT.json';result=read(rp) if rp.exists() else None
    plan={x['id']:x for x in s.schedule(phase)};gold=read(s.input_dir(phase)/'HOST_GOLD.json')
    prefixes=read(s.input_dir(phase)/'PREFIXES.json')
    native=[read(p) for p in sorted((directory/'science/native-calls').glob('*-result.json'))]
    starts=[read(p) for p in sorted((directory/'science/native-calls').glob('*-start.json'))]
    startmap={x['index']:x for x in starts};indices={x['index'] for x in native}
    assert len(startmap)==len(starts) and len(indices)==len(native) and indices<=set(startmap)
    bp=directory/'owned-service/BINDING.json';binding=read(bp) if bp.exists() else None
    expected=s.read(s.train.OUTPUT/'checkpoint-0001/EVAL_BINDING.json') if arm=='updated' else s.read(s.BASELINES[phase]/'owned-service/BINDING.json')
    errors=[]
    if binding is not None and binding!=expected:errors.append('service_binding_changed')
    contract=directory/'science/TERMINAL_STRIP_CONTRACT.json'
    if contract.exists() and read(contract)!=c.hooks.qualify():errors.append('terminal_hook_contract_changed')
    returned=[x for x in native if x['status']=='returned'];tok,render,vocab=renderer()
    stops={render._im_end,render._endoftext};decoded={};provider_ids=[]
    with c.hooks.installed():
        for n in native:
            assert all(n.get(k)==v for k,v in startmap[n['index']].items())
            if n['status']!='returned':continue
            payload=n['response'];c.source.validate_native_response(payload)
            ids=payload['tokens']['completion_ids'];prompt=payload['tokens']['prompt_ids']
            assert all(t<vocab for t in prompt+ids)
            assert payload['model']==n['model']==expected['role_map']['root']
            assert n['evidence']['completion_ids_sha256']==digest(ids)
            assert payload['usage']['prompt_tokens']==len(prompt) and payload['usage']['completion_tokens']==len(ids)
            assert len(ids)<=2048 and len(prompt)+len(ids)<=8192
            sam=n['sampling'];assert sam['temperature']==.5 and sam['top_p']==1 and sam['max_tokens']==2048
            assert sam['extra_body']['top_k']==-1 and sam['extra_body']['min_p']==0
            parsed=render.parse_response(ids)
            assert (parsed.content or None)==payload['message']['content']
            assert (parsed.reasoning_content or None)==payload['message']['reasoning_content']
            from verifiers.v1.clients.train import response_from_generate
            rebuilt=response_from_generate(dict(content=parsed.content,reasoning_content=parsed.reasoning_content,
                tool_calls=parsed.tool_calls,prompt_ids=prompt,completion_ids=ids,
                completion_logprobs=payload['tokens']['completion_logprobs'],finish_reason=payload['finish_reason']),n['model'])
            tools=[{'name':x.name,'arguments':x.arguments} for x in (rebuilt.message.tool_calls or [])]
            actual_tools=[{k:x.get(k) for k in ('name','arguments')} for x in (payload['message']['tool_calls'] or [])]
            # Exercise the actual object-to-wire conversion, including nameless invalid-tool filtering.
            # Preserve unfiltered parser status below so dropped invalid blocks are not called bare finals.
            assert tools==actual_tools
            before=ids[:next((i for i,t in enumerate(ids) if t in stops),len(ids))]
            wire=tok.decode(before,skip_special_tokens=False)
            bare=not parsed.tool_calls and not parsed.reasoning_content and not any(t in tok.all_special_ids for t in before)
            bare=bare and not any(z in wire for z in ('<think>','</think>','<tool_call>','</tool_call>'))
            decoded[n['index']]=dict(bare=bare,wire=wire,native=payload['message']['content'],tool_calls=tools,
                valid_final_text=not parsed.tool_calls and isinstance(parsed.content,str),
                raw_tool_parse_status=[str(x.status) for x in parsed.tool_calls or []])
            provider_ids.append(payload['id'])
    if len(provider_ids)!=len(set(provider_ids)):errors.append('duplicate_provider_ids')
    rows={};mapped=set();trace_ids=set()
    for p in sorted((directory/'science/episodes').glob('*.json')):
        item=read(p);coord=item['coordinate'];ident=coord['id'];assert coord==plan[ident] and p.stem==ident and ident not in rows
        raw=item['episode'];assert digest(raw)==item['episode_sha256']
        traces=raw.get('traces') or [];trace=traces[0] if len(traces)==1 else {}
        if trace.get('id'):assert trace['id'] not in trace_ids;trace_ids.add(trace['id'])
        truth=gold[coord['record_id']];reply=trace.get('root_reply')
        ours=c.source.inspect_trace(raw,truth,native,prefixes[ident]['token_ids'],
                                    censored=item['derived'].get('terminal_status')=='deadline_censored')
        for key in ('scientifically_available','raw_exact','reward','native_mapping_complete','initial_root_prefix_verified'):
            if ours[key]!=item['derived'][key]:errors.append(f'collector_recomputation:{ident}:{key}')
        available=ours['scientifically_available'];exact=isinstance(reply,str) and reply==truth['answer']
        score=helper().official_grade(reply,truth['answer'],truth['random_string_to_prepend'])
        if available and not math.isclose(score,ours['reward'],abs_tol=1e-12):errors.append('official_score:'+ident)
        session=sorted((n for n in native if n.get('session_id')==trace.get('id')),key=lambda x:x['index'])
        ret=[n for n in session if n['status']=='returned']
        for n in session:assert n['sampling']['seed']==coord['seed']
        mapping=ours['causal_mapping'];cost=helper().role_cost(ret,mapping)
        for match in mapping.get('matches') or []:
            idx=match['audit_index']
            if 0<=idx<len(ret):mapped.add(ret[idx]['index'])
        obs=[n['message']['content'] for n in trace.get('nodes') or []
             if n.get('message',{}).get('role')=='tool' and isinstance(n['message'].get('content'),str)]
        programs=[{'name':t.get('name'),'arguments':t.get('arguments')} for n in trace.get('nodes') or []
                  for t in n.get('message',{}).get('tool_calls') or [] if t.get('name')=='ipython']
        mechanism=helper().mechanism(obs,reply,truth['answer'],truth['random_string_to_prepend'])
        if not available:mechanism['category']='unavailable'
        finals=[decoded[n['index']] for n in ret if not decoded[n['index']]['tool_calls']]
        last=finals[-1] if finals else None
        native_to_root=bool(last and (last['native'] or '')==(reply or ''))
        if trace.get('stop_condition')=='agent_completed' and last and not native_to_root:
            errors.append('final_native_root_disagreement:'+ident)
        raw_exact=bool(last and last['bare'] and last['wire']==truth['answer'])
        copy_type=('unavailable' if not available else 'exact' if exact else
                   'invalid_or_no_final_text' if not last or not last['valid_final_text'] else
                   'edge_whitespace_difference' if isinstance(reply,str) and reply.strip()==truth['answer'].strip()
                   else 'other_copy_difference' if mechanism['clean_target_observed'] else 'no_clean_target_evidence')
        rows[ident]=dict(coordinate=coord,available=available,raw_exact=exact,official_score=score if available else None,
            stop=trace.get('stop_condition'),failure_class=ours['failure_class'],
            initial_prefix_exact=ours['initial_root_prefix_verified'],cost=cost,mechanism=mechanism,
            final_bare_native_exact=raw_exact,actual_final_text=bool(last and last['valid_final_text']),
            actual_bare_final=bool(last and last['bare']),
            native_final_matches_root=native_to_root,copy_type=copy_type,
            final_sha256=digest(reply),programs_sha256=digest(programs),observations_sha256=digest(obs),
            native_actions=[dict(status=n['status'],prompt_sha256=digest(n.get('response',{}).get('tokens',{}).get('prompt_ids')),
                action_sha256=digest(n.get('response',{}).get('tokens',{}).get('completion_ids')),
                model=n['model'],sampling=n['sampling']) for n in session],
            episode_path=str(p),episode_file_sha256=sha(p))
    physical=dict(started=len(starts),result_records=len(native),returned=len(returned),
        error_results=len(native)-len(returned),start_only=len(set(startmap)-indices),
        orphan_returned=len({n['index'] for n in returned}-mapped),
        prompt_tokens=sum(len(n['response']['tokens']['prompt_ids']) for n in returned),
        completion_tokens=sum(len(n['response']['tokens']['completion_ids']) for n in returned),
        unknown_usage_calls=len(starts)-len(returned),cost_semantics='Observed returned-token subtotal; errors/start-only costs unknown')
    policy={role:{k:sum(r['cost'][role][k] for r in rows.values()) for k in ('calls','prompt_tokens','completion_tokens')} for role in ('root','child')}
    available=sum(r['available'] for r in rows.values());correct=sum(r['available'] and r['raw_exact'] for r in rows.values())
    if result and (result['scientifically_available']!=available or result['raw_exact']!=correct):errors.append('result_totals_disagree')
    qualified=bool(terminal.get('complete') and terminal.get('released') and not errors and len(rows)==len(plan) and available==len(plan))
    return dict(phase=phase,arm=arm,planned=len(plan),recorded=len(rows),available=available,correct=correct,
        wrong=available-correct,unavailable=len(plan)-available,missing_coordinates=sorted(set(plan)-set(rows)),
        initial_prefix_verified=sum(r['initial_prefix_exact'] for r in rows.values()),
        mechanism_counts=dict(Counter(r['mechanism']['category'] for r in rows.values())),
        copy_types=dict(Counter(r['copy_type'] for r in rows.values())),rows=rows,physical=physical,policy=policy,
        owner=terminal,collector_result=result,qualified=qualified,integrity_errors=errors)

def pair(plan,left,right):
    pairs=[];contexts={}
    for coord in plan:
        a=left.get(coord['id']);b=right.get(coord['id']);both=bool(a and b and a['available'] and b['available'])
        if a and b:assert a['coordinate']==b['coordinate']==coord
        win=bool(both and b['raw_exact'] and not a['raw_exact']);loss=bool(both and a['raw_exact'] and not b['raw_exact'])
        paths=bool(a and b and a['native_actions'] and len(a['native_actions'])==len(b['native_actions']) and
            all(x['status']==y['status'] and x['prompt_sha256']==y['prompt_sha256'] and x['action_sha256']==y['action_sha256']
                for x,y in zip(a['native_actions'],b['native_actions'])))
        row=dict(coordinate=coord,paired_available=both,win=win,loss=loss,
            old_exact=a['raw_exact'] if a and a['available'] else None,new_exact=b['raw_exact'] if b and b['available'] else None,
            native_token_paths_equal_descriptive_only=paths,
            programs_equal=bool(a and b and a['programs_sha256']==b['programs_sha256']),
            observations_equal=bool(a and b and a['observations_sha256']==b['observations_sha256']),
            old_mechanism=a['mechanism']['category'] if a else 'unattempted',new_mechanism=b['mechanism']['category'] if b else 'unattempted')
        pairs.append(row);contexts.setdefault(coord['record_id'],[]).append(row)
    grouped=[dict(record_id=k,planned_repeats=len(v),paired_available=sum(r['paired_available'] for r in v),
        complete=all(r['paired_available'] for r in v),paired_net_correct=sum(int(r['win'])-int(r['loss']) for r in v)) for k,v in contexts.items()]
    return dict(planned=len(plan),paired_available=sum(p['paired_available'] for p in pairs),
        unknown_pairs=sum(not p['paired_available'] for p in pairs),wins=sum(p['win'] for p in pairs),losses=sum(p['loss'] for p in pairs),
        context_units=len(contexts),complete_context_pairs=sum(g['complete'] for g in grouped),
        contexts_with_positive_paired_delta=sum(g['complete'] and g['paired_net_correct']>0 for g in grouped),
        contexts_with_negative_paired_delta=sum(g['complete'] and g['paired_net_correct']<0 for g in grouped),
        contexts=grouped,pairs=pairs)

def build():
    c=bindings();s=c.study
    pending=[phase for phase in s.CAPS if not (SIDE/f'outputs/{phase}-001/OWNER_TERMINAL.json').exists()]
    if pending:return dict(status='PENDING_OWNER_TERMINALS',pending=pending,polling=False,GPU_calls=0)
    c.checkpoint.verify_checkpoint();phases={}
    for phase in s.CAPS:
        old=stage(phase,'cp32');new=stage(phase,'updated')
        phases[phase]=dict(cp32=old,updated=new,pairing=pair(s.schedule(phase),old['rows'],new['rows']))
    full=all(x[a]['qualified'] for x in phases.values() for a in ('cp32','updated'))
    training=read(s.train.OUTPUT/'RESULT.json');training_owner=read(s.train.OUTPUT/'OWNER_TERMINAL.json')
    return dict(status='COMPLETE_PAIRED_AUDIT' if full else 'TERMINAL_PARTIAL_OR_INTEGRITY_HOLD',phases=phases,
        planned_per_arm=48,context_units={'held':16,'long':16},training=training,training_owner=training_owner,
        training_cost_separate=True,source_sha256=dict(PINS),source_READY_sha256=SOURCE_READY_SHA,
        GPU_calls=0,generated_programs_executed=False,
        interpretation='Different weights: identical native arrays are descriptive, never a clamp-only or lossless-transport causal comparison. Clean stdout is observed information, not proof of internal retrieval. Research-exposed panels; base pretraining unknown.')

def markdown(r):
    if r['status'].startswith('PENDING'):return '# Fixed-baseline RL readout\n\nPending owner terminals: '+', '.join(r['pending'])+'. One check only; no polling.\n'
    out=['# Fixed-baseline final-decision RL readout','',r['status'],'']
    for phase,x in r['phases'].items():
        a=x['cp32'];b=x['updated'];p=x['pairing']
        out += [f"{phase}: cp32 {a['correct']}/{a['planned']} correct ({a['available']} available); RL {b['correct']}/{b['planned']} correct ({b['available']} available). {p['wins']} wins, {p['losses']} losses among {p['paired_available']} available pairs; {p['unknown_pairs']} unknown. {p['context_units']} context units, {p['complete_context_pairs']} complete paired contexts.",
            f"Clean-target/copy taxonomy: cp32 {a['mechanism_counts']}; RL {b['mechanism_counts']}.",
            f"Physical returned calls/tokens: cp32 {a['physical']['returned']} / {a['physical']['prompt_tokens']} input + {a['physical']['completion_tokens']} output; RL {b['physical']['returned']} / {b['physical']['prompt_tokens']} input + {b['physical']['completion_tokens']} output. Unknown-cost calls {a['physical']['unknown_usage_calls']} / {b['physical']['unknown_usage_calls']}. Owner seconds {a['owner']['elapsed_seconds']:.2f} / {b['owner']['elapsed_seconds']:.2f}.",'']
    out += [f"Training cost is separate: {r['training']['elapsed_seconds']:.2f}s science, {r['training_owner']['elapsed_seconds']:.2f}s owner, one optimizer step.",'',r['interpretation'],'',
        'Scores and native token decoding are recomputed; causal mapping/failure classification and clean-observation definitions reuse reviewed helpers. No generated program was executed. No checkpoint, example or threshold was selected from this readout.']
    return '\n'.join(out)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','check']);p.add_argument('--output',type=Path);a=p.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';r=verify()
    if a.command=='verify':print(r['identity'])
    else:
        report=build();report['analyzer_READY_sha256']=sha(ROOT/'READY.json');report['created_epoch']=time.time()
        if a.output:write(a.output,report);write(a.output.with_suffix('.md'),markdown(report))
        print({'status':report['status'],'pending':report.get('pending')})
