"""Fixed eight-group raw reward/mechanism analysis; no rollout, optimizer or polling."""
import argparse
import ast
from collections import Counter
import functools
import hashlib
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
SIDE=STORE/'sidecars/openai-mrcr-procedural-sft32-onpolicy-screen-v1'
PINS={}
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):PINS[str(path)]=sha(path);return json.loads(Path(path).read_text())
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def write(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('x') as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')

@functools.lru_cache(None)
def bindings():
    source=read(ROOT/'SOURCE.json');sys.path.insert(0,str(SIDE))
    module=importlib.import_module(source['collector_module'])
    assert Path(module.__file__).resolve()==SIDE/(source['collector_module']+'.py')
    return module

def actual_final_text(trace,message,available):
    return bool(available and trace.get('stop_condition')=='agent_completed' and isinstance(trace.get('root_reply'),str)
                and trace['root_reply'] and not message.get('tool_calls') and isinstance(message.get('content'),str)
                and message['content']==trace['root_reply'])

def group_summary(samples):
    known=[s for s in samples if s['available']];complete=len(samples)==len(known)==4
    rewards=[s['binary_reward'] for s in known];p=sum(rewards)/len(rewards) if rewards else None
    answers=[s['returned_final_sha256'] for s in known if s['actual_final_text']]
    counts=Counter(answers);n=len(answers)
    entropy=-sum((v/n)*math.log(v/n) for v in counts.values()) if n else None
    return {'planned':4,'recorded':len(samples),'available':len(known),'complete_group':complete,
        'binary_rewards':rewards,'binary_population_variance':p*(1-p) if complete else None,
        'observed_available_variance_diagnostic':p*(1-p) if p is not None else None,
        'mixed_reward':complete and 0<sum(rewards)<4,
        'all_correct':complete and sum(rewards)==4,'all_incorrect':complete and sum(rewards)==0,
        'rloo_advantages':[(4*r-sum(rewards))/3 for r in rewards] if complete else None,
        'unique_available_actual_final_answers':len(counts),'empirical_four_sample_answer_entropy_nats':entropy,
        'same_first_program':complete and len({s['first_program_sha256'] for s in known})==1,
        'same_first_native_path':complete and len({s['first_native_path_sha256'] for s in known})==1,
        'all_clean_target_stdout':complete and all(s['clean_target_stdout'] for s in known),
        'failure_categories':dict(Counter(s['failure_category'] for s in samples)),
        'missing_unknown_not_imputed_as_reward_zero':True}

def code_features(trace,teacher):
    programs=[]
    for node in trace.get('nodes',[]):
        for call in (node.get('message') or {}).get('tool_calls') or []:
            if call.get('name')!='ipython':continue
            args=call.get('arguments');args=json.loads(args) if isinstance(args,str) else args
            code=(args or {}).get('code','');parsed=None
            try:parsed=ast.parse(code)
            except (SyntaxError,TypeError):pass
            programs.append({'code_sha256':digest(code),'characters':len(code),'ast_parseable':parsed is not None,
                'teacher_AST_exact':bool(parsed is not None and teacher and ast.dump(parsed)==ast.dump(ast.parse(teacher))),
                'reads_context_json':bool(parsed is not None and any(isinstance(n,ast.Constant) and n.value=='/context.json' for n in ast.walk(parsed)))})
    return programs

def episode(item,native,gold,prefix,teacher,collector,tokenizer,renderer):
    raw=item['episode'];assert digest(raw)==item['episode_sha256']
    traces=raw.get('traces') or [];trace=traces[0] if len(traces)==1 else {}
    derived=collector.original_inspect_trace(raw,gold,native,prefix)
    for key in ('raw_exact','scientifically_available','reward','native_mapping_complete','initial_root_prefix_verified'):
        assert derived[key]==item['derived'][key],key
    available=derived['scientifically_available'];final=trace.get('root_reply');answer=gold['answer']
    observations=[n['message'].get('content') or '' for n in trace.get('nodes',[]) if n.get('message',{}).get('role')=='tool']
    target=answer.removeprefix(gold['random_string_to_prepend'])
    clean=any(text in (answer,answer+'\n',target,target+'\n') for text in observations)
    programs=code_features(trace,teacher)
    rows=sorted((r for r in native if r.get('session_id')==trace.get('id') and r.get('model')==collector.study.ADAPTED_ALIAS and r['status']=='returned'),key=lambda r:r['index'])
    turns=[];vocab_size=len(tokenizer)
    for i,r in enumerate(rows):
        payload=r['response'];tokens=payload['tokens'];ids=tokens['completion_ids'];logs=tokens['completion_logprobs']
        assert digest(ids)==r['evidence']['completion_ids_sha256'] and len(ids)==len(logs)
        assert all(type(t)is int and 0<=t<vocab_size for t in ids+tokens['prompt_ids'])
        assert all(math.isfinite(x) and x<=0 for x in logs)
        with collector.hooks.installed():parsed=renderer.parse_response(ids)
        assert (parsed.content or None)==payload['message']['content']
        message=payload['message'];last=i==len(rows)-1
        final_turn=last and actual_final_text(trace,message,available) and not parsed.tool_calls
        stops={renderer._im_end,renderer._endoftext};j=next((i for i,t in enumerate(ids) if t in stops),len(ids))
        bare=not parsed.tool_calls and not parsed.reasoning_content and not any(t in tokenizer.all_special_ids for t in ids[:j])
        wire=tokenizer.decode(ids[:j],skip_special_tokens=False)
        bare=bare and not any(x in wire for x in ('<think>','</think>','<tool_call>','</tool_call>','<tool_response>','</tool_response>'))
        turns.append({'position':i,'native_index':r['index'],'prompt_tokens':len(tokens['prompt_ids']),'action_tokens':len(ids),
            'prompt_ids_sha256':digest(tokens['prompt_ids']),'action_ids_sha256':digest(ids),'sampling':r['sampling'],
            'actual_final_text_turn':final_turn,'last_root_action':last,'parsed_tool_count':len(parsed.tool_calls),
            'tool_parse_statuses':[str(t.status) for t in parsed.tool_calls],'reasoning_present':bool(parsed.reasoning_content),
            'bare_semantic_final_span':bool(final_turn and bare),'bare_exact':bool(final_turn and bare and wire==answer),
            'native_chosen_logprob_sum':sum(logs),'native_mean_chosen_token_surprisal_nats':-sum(logs)/len(logs),
            'native_min_chosen_logprob':min(logs),'native_max_chosen_logprob':max(logs),
            'full_token_distribution_entropy':None})
    actual=bool(turns and turns[-1]['actual_final_text_turn'])
    category=('unknown' if not available else 'returned_exact' if derived['raw_exact'] else
        'copy_difference' if clean and actual else 'correct_stdout_no_text_final' if clean else
        'retrieval_or_program_failure' if programs else 'no_program_or_invalid_final')
    return {'coordinate':item['coordinate'],'available':available,'binary_reward':int(derived['raw_exact']) if available else None,
        'official_score':derived['reward'],'failure_category':category,'collector_failure_class':derived['failure_class'],
        'stop_condition':trace.get('stop_condition'),'raw_ok':raw.get('ok'),
        'returned_final_sha256':digest(final),'returned_final_characters':len(final) if isinstance(final,str) else None,
        'actual_final_text':actual,'clean_target_stdout':clean,'programs':programs,
        'first_program_sha256':programs[0]['code_sha256'] if programs else None,
        'first_native_path_sha256':digest([turns[0]['prompt_ids_sha256'],turns[0]['action_ids_sha256']]) if turns else None,
        'first_teacher_AST_exact':programs[0]['teacher_AST_exact'] if programs else False,
        'observation_utf8_bytes':sum(len(s.encode()) for s in observations),'tool_error_count':sum('Traceback' in s for s in observations),
        'turns':turns,'root_actions':derived['root_actions_returned'],'child_actions':derived['child_actions_returned'],
        'last_root_action_is_not_final_text':bool(turns and not turns[-1]['actual_final_text_turn'])}

def verify():
    ready=read(ROOT/'READY.json');assert ready['identity']==digest({k:v for k,v in ready.items() if k!='identity'})
    for p,w in ready['closure_sha256'].items():assert sha(p)==w,p
    return ready

def build():
    desc=read(ROOT/'SOURCE.json');out=Path(desc['output'])
    if not (out/'OWNER_TERMINAL.json').exists():return {'status':'PENDING','one_check_no_polling':True}
    terminal=read(out/'OWNER_TERMINAL.json');c=bindings();s=c.study
    if (out/'science/TERMINAL_STRIP_CONTRACT.json').exists():assert read(out/'science/TERMINAL_STRIP_CONTRACT.json')==c.hooks.qualify()
    result=read(out/'science/RESULT.json') if (out/'science/RESULT.json').exists() else None
    bindingpath=out/'owned-service/BINDING.json'
    if bindingpath.exists():assert read(bindingpath)==read(Path(desc['binding_source']))
    plan=s.schedule('train');planbyid={x['id']:x for x in plan};gold=read(s.input_dir('train')/'HOST_GOLD.json');prefix=read(s.input_dir('train')/'PREFIXES.json')
    corpus=read(STORE/'sidecars/openai-mrcr-procedural-sft-warmstart-v1/TEACHER_CORPUS_V2.json')
    teachers={x['episode_id']:x['teacher']['authored_code'] for x in corpus['episodes']}
    native=[read(p) for p in sorted((out/'science/native-calls').glob('*-result.json'))]
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    tokenizer=AutoTokenizer.from_pretrained(str(s.BASE),local_files_only=True);renderer=Qwen3Renderer(tokenizer)
    samples=[];seen=set()
    for p in sorted((out/'science/episodes').glob('*.json')):
        item=read(p);coordinate=item['coordinate'];assert coordinate==planbyid[coordinate['id']]
        assert coordinate['id'] not in seen;seen.add(coordinate['id'])
        sample=episode(item,native,gold[coordinate['record_id']],prefix[coordinate['id']]['token_ids'],teachers[coordinate['record_id']],c,tokenizer,renderer)
        sample['episode_sha256']=sha(p);samples.append(sample)
    groups=[]
    for record in s.records('train'):
        values=sorted((v for v in samples if v['coordinate']['record_id']==record['id']),key=lambda v:v['coordinate']['repeat'])
        groups.append({'record_id':record['id'],**group_summary(values),'samples':values})
    complete=sum(g['complete_group'] for g in groups);mixed=sum(g['mixed_reward'] for g in groups)
    copy_mixed=sum(g['mixed_reward'] and g['all_clean_target_stdout'] and g['same_first_native_path'] for g in groups)
    allcorrect=complete==8 and all(g['all_correct'] for g in groups)
    qualified=terminal.get('complete') is True and terminal.get('released') is True
    decision=('INCOMPLETE_OR_UNQUALIFIED_NO_GLOBAL_PROMOTION' if complete<8 or not qualified else 'HARDER_PREDECLARED_TRAIN_DATA_PROPOSAL' if allcorrect else
        'QUALIFIED_RL_OBJECTIVE_COMPARISON_CANDIDATE_COPY_DOMINATED' if mixed>=2 and copy_mixed==mixed else
        'QUALIFIED_ALL_ROOT_RL_CANDIDATE' if mixed>=2 else 'INSUFFICIENT_G4_CONTRAST_REVIEW_DIVERSITY_BEFORE_EXPLORATION_CHANGE')
    returned=[r for r in native if r['status']=='returned'];started=len(list((out/'science/native-calls').glob('*-start.json')))
    return {'status':'TERMINAL_G4_AUDIT','planned_groups':8,'group_size':4,'planned_episodes':32,'recorded':len(samples),
        'available':sum(v['available'] for v in samples),'raw_exact_available':sum(v['binary_reward'] or 0 for v in samples),
        'recorded_unavailable':sum(not v['available'] for v in samples),'unrecorded':32-len(samples),
        'unrecorded_coordinate_ids':sorted(set(planbyid)-seen),'owner_qualified':qualified,
        'complete_groups':complete,'mixed_groups':mixed,'same_first_path_clean_stdout_mixed_groups':copy_mixed,'groups':groups,
        'decision_proposal_not_training_admission':decision,'physical':{'started':started,'returned':len(returned),
            'errors':sum(r['status']!='returned' for r in native),'start_only':started-len(native),
            'observed_prompt_tokens':sum(len(r['response']['tokens']['prompt_ids']) for r in returned),
            'observed_completion_tokens':sum(len(r['response']['tokens']['completion_ids']) for r in returned),
            'unreturned_cost_unknown_calls':started-len(returned),'costs_are_observed_subtotals':True},
        'owner':terminal,'collector_result':result,'source_sha256':dict(PINS),'GPU_calls':0,'optimizer_steps':0,
        'limits':['Binary rewards are recomputed raw_exact, not legacy continuous derived.reward.',
            'Native chosen-token logprobs/surprisal are not full-distribution entropy or independently HF-qualified behavior probabilities.',
            'Answer entropy is empirical from at most4 available final strings, not a policy entropy estimate.',
            'Last root action is not final-only credit unless it is an actual committed text final.',
            'Eight previously trained contexts, no heldout accuracy/generalization claim; no adaptive resampling or gradient authority.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','check']);p.add_argument('--output',type=Path);a=p.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';ready=verify()
    if a.command=='verify':print({'identity':ready['identity']})
    else:
        report=build();report['analyzer_READY_sha256']=sha(ROOT/'READY.json');report['created_epoch']=time.time()
        if a.output:write(a.output,report)
        print({k:v for k,v in report.items() if k in ('status','complete_groups','mixed_groups','raw_exact_available','decision_proposal_not_training_admission')})
