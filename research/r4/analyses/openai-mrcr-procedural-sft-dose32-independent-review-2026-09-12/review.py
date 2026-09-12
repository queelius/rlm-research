"""Bounded inert review of fixed held SFT32 scores and exact token fidelity."""
from collections import Counter,defaultdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path

STORE=Path('/project/alex_phd/runs/rlm-research-r4')
SOURCE=STORE/'analyses/openai-mrcr-procedural-sft-dose32-readout-2026-09-12'
ROOT=Path(__file__).resolve().parent
PINS={}
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):
    PINS[str(path)]=sha(path);return json.loads(Path(path).read_text())
def textsha(value):return hashlib.sha256(value.encode()).hexdigest()
def write(path,value):
    with Path(path).open('x') as f:json.dump(value,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    report=read(SOURCE/'main-final-held-snapshot-001/REPORT.json')
    decoder=read(SOURCE/'HELD_DECODER_SEAM_V2.json')
    closure={}
    for group in (report['source_sha256'],decoder['source_sha256']):
        for path,want in group.items():
            assert path not in closure or closure[path]==want,path
            closure[path]=want
    for path,want in closure.items():assert sha(path)==want,path
    assert report['integrity_errors']==[] and report['held_gate_open'] is True
    scorepath=STORE/'sidecars/openai-mrcr-short-root-data-v1/official_score.py'
    spec=importlib.util.spec_from_file_location('dose32_review_official_score',scorepath)
    scoring=importlib.util.module_from_spec(spec);spec.loader.exec_module(scoring)
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    model=STORE.parents[1]/'research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554'
    tokenizer=AutoTokenizer.from_pretrained(str(model),local_files_only=True)
    renderer=Qwen3Renderer(tokenizer);stops={renderer._im_end,renderer._endoftext}
    golds=read(STORE/'sidecars/openai-mrcr-procedural-sft-eval-v1/inputs/held/HOST_GOLD.json')
    summaries={};rows={};contexts=defaultdict(dict);parser_replays=0
    for arm in ('held_base','held_checkpoint32'):
        stage=report['stages'][arm];out=Path(stage['attempt'])/'science/native-calls'
        native={str(p):read(p) for p in sorted(out.glob('*-result.json'))}
        native_by_trace=defaultdict(list)
        for p,n in native.items():native_by_trace[n.get('session_id') or n.get('turn',{}).get('trace_id')].append((p,n))
        returned=[n for n in native.values() if n['status']=='returned']
        errors=[{'file':p,'type':n['error']['type'],'message':n['error']['message']} for p,n in native.items() if n['status']!='returned']
        prompt=sum(len(n['response']['tokens']['prompt_ids']) for n in returned)
        completion=sum(len(n['response']['tokens']['completion_ids']) for n in returned)
        assert prompt==stage['collector_result']['prompt_tokens']
        assert completion==stage['collector_result']['completion_tokens']
        for n in returned:
            assert n['response']['usage']['prompt_tokens']==len(n['response']['tokens']['prompt_ids'])
            assert n['response']['usage']['completion_tokens']==len(n['response']['tokens']['completion_ids'])
        drows={r['coordinate_id']:r for r in decoder['arms'][arm]['rows']}
        armrows=[]
        for old in stage['rows']:
            d=drows[old['coordinate_id']];item=read(Path(old['episode_path']));trace=item['episode']['traces'][0]
            gold=golds[old['record_id']];final=trace.get('root_reply')
            exact=isinstance(final,str) and final==gold['answer']
            assert exact==old['raw_exact']==d['original_raw_exact']
            if old['available'] and final:
                assert scoring.grade(final,gold['answer'],gold['random_string_to_prepend'])==old['official_score']
            obs=[n['message']['content'] for n in trace['nodes'] if n.get('message',{}).get('role')=='tool']
            target=gold['answer'].removeprefix(gold['random_string_to_prepend'])
            clean=any(t in (target,target+'\n',gold['answer'],gold['answer']+'\n') for t in obs)
            assert clean==old['retrieval_copy']['clean_correct_target_observed']
            raw_exact=None;trim_lost=False;stop_positions=[]
            if d['native_final_present']:
                n=native[d['native_path']];ids=n['response']['tokens']['completion_ids']
                assert n['session_id']==trace['id'] and n['model']==trace['agent']['config']['model']
                tokenhash=hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()
                assert tokenhash==n['evidence']['completion_ids_sha256']==d['completion_ids_sha256']
                parsed=renderer.parse_response(ids);parser_replays+=1
                saved=n['response']['message']['content']
                assert (parsed.content or None)==saved and (saved or '')==(final or '')
                stop_positions=[i for i,t in enumerate(ids) if t in stops]
                before=ids[:stop_positions[0]] if stop_positions else ids
                wire=tokenizer.decode(before,skip_special_tokens=False)
                assert textsha(wire)==d['raw_action_before_stop_utf8_sha256']
                bare=not any(t in tokenizer.all_special_ids for t in before) and not parsed.tool_calls and not parsed.reasoning_content
                bare=bare and not any(m in wire for m in ('<think>','</think>','<tool_call>','</tool_call>','<tool_response>','</tool_response>'))
                assert bare==d['bare_semantic_final_span']
                if bare:
                    raw_exact=wire==gold['answer'];assert raw_exact==d['bare_semantic_exact_DIAGNOSTIC_ONLY']
                    trim_lost=raw_exact and not exact
                    if trim_lost:assert wire.strip()==saved==final and wire.endswith('  ') and not wire.startswith(' ')
            matches=native_by_trace[trace['id']]
            unavailable_errors=[n['error']['message'] for _,n in matches if n['status']!='returned']
            row={'coordinate_id':old['coordinate_id'],'record_id':old['record_id'],'seed':old['seed'],
                'available':old['available'],'returned_exact':exact,'raw_token_exact':raw_exact,
                'trailing_two_spaces_lost_exact':trim_lost,'clean_correct_target_stdout':clean,
                'failure_class':old['failure_class'],'stop_condition':trace['stop_condition'],
                'native_error_messages':unavailable_errors,'final_stop_positions':stop_positions,
                'episode_sha256':sha(old['episode_path']),'final_utf8_sha256':textsha(final) if isinstance(final,str) else None}
            armrows.append(row);contexts[old['record_id']].setdefault(arm,[]).append(row)
        assert len(armrows)==32
        rows[arm]={r['coordinate_id']:r for r in armrows}
        summaries[arm]={'planned':32,'recorded':32,'available':sum(r['available'] for r in armrows),
            'returned_exact':sum(r['returned_exact'] and r['available'] for r in armrows),
            'raw_token_exact_diagnostic':sum(r['raw_token_exact'] is True for r in armrows),
            'trailing_two_spaces_lost_exact':sum(r['trailing_two_spaces_lost_exact'] for r in armrows),
            'clean_correct_target_stdout':sum(r['clean_correct_target_stdout'] for r in armrows),
            'category_counts':decoder['arms'][arm]['category_counts'],'rows':armrows,
            'cost':{'physical_starts':len(list(out.glob('*-start.json'))),'native_returned':len(returned),
                'native_errors':errors,'observed_prompt_tokens':prompt,'observed_completion_tokens':completion,
                'errors_without_usage':len(errors),'owner_seconds':stage['owner_terminal']['elapsed_seconds'],
                'collector_usage_unknown_calls_counts_returned_only':stage['collector_result']['usage_unknown_calls']},
            'official_score_sum_available':sum(r['official_score'] or 0 for r in stage['rows'] if r['available'])}
    pair=[]
    for ident,x in rows['held_base'].items():
        y=rows['held_checkpoint32'][ident];assert (x['record_id'],x['seed'])==(y['record_id'],y['seed'])
        both=x['available'] and y['available']
        pair.append({'coordinate_id':ident,'record_id':x['record_id'],'paired_available':both,
            'cp_win':both and y['returned_exact'] and not x['returned_exact'],
            'cp_loss':both and x['returned_exact'] and not y['returned_exact']})
    wins=sum(p['cp_win'] for p in pair);losses=sum(p['cp_loss'] for p in pair)
    assert (wins,losses)==(15,0) and sum(p['paired_available'] for p in pair)==29
    contextrows=[]
    for ident,arms in sorted(contexts.items()):
        assert all(len(v)==2 for v in arms.values())
        contextrows.append({'record_id':ident,
            'returned_exact_by_arm':{a:sum(r['returned_exact'] for r in v) for a,v in arms.items()},
            'available_by_arm':{a:sum(r['available'] for r in v) for a,v in arms.items()},
            'clean_target_by_arm':{a:sum(r['clean_correct_target_stdout'] for r in v) for a,v in arms.items()},
            'paired_wins':sum(p['cp_win'] for p in pair if p['record_id']==ident),
            'paired_losses':sum(p['cp_loss'] for p in pair if p['record_id']==ident)})
    result={'source_report_sha256':sha(SOURCE/'main-final-held-snapshot-001/REPORT.json'),
        'decoder_V2_sha256':sha(SOURCE/'HELD_DECODER_SEAM_V2.json'),'declared_union_hashes_verified':len(closure),
        'actual_parser_replays':parser_replays,'arms':summaries,'paired_available':29,'paired_wins':wins,'paired_losses':losses,
        'contexts':contextrows,'contexts_with_paired_wins':sum(r['paired_wins']>0 for r in contextrows),
        'independent_unit_limit':'16 contexts with two repeats, not 32 independent items; common fewshot and adaptive campaign exposure remain',
        'training_checkpoint_qualification':'trusted previously reviewed evaluator chain; no independent Adam/backprop replay here',
        'availability_qualification':'retains reviewed collector causal-mapping gate; unavailable raw errors checked, not recoded as wrong',
        'source_sha256':{**PINS,str(__file__):sha(__file__)},'GPU_calls':0,'generated_code_executed':False}
    write(ROOT/'REVIEW.json',result)
    print({'declared_hashes_verified':len(closure),'parser_replays':parser_replays,'wins':wins,'losses':losses,
           'contexts_with_paired_wins':result['contexts_with_paired_wins'],
           'arms':{a:{k:v for k,v in d.items() if k not in ('rows',)} for a,d in summaries.items()}})

if __name__=='__main__':main()
