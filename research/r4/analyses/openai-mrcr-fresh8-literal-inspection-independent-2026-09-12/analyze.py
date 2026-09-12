"""Matched raw32 audit; request-observation candidates require inert manual use adjudication."""
import argparse
import ast
from collections import Counter
import difflib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
SIDE=STORE/'sidecars/openai-mrcr-fresh8-literal-inspection-v1'
CONTROL=STORE/'sidecars/openai-mrcr-procedural-sft32-fresh8-onpolicy-screen-v1'
OLD_AUDIT=ROOT.parent/'openai-mrcr-sft32-fresh8-g4-mechanism-2026-09-12/REPORT.json'
CORE=ROOT.parent/'openai-mrcr-sft32-g4-mechanism-2026-09-12/analyze.py'
SIDE_SHA='575aaf1ebc3f27bd79f9da0673d3babefab373a403da992768c98abe5b173b3d'
OLD_SHA='e8b0ae49b29415130e990d62cface02ab9d330b0b983d5b9db504c683d913f19'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


core=load('literal_audit_proven_core',CORE)


def bindings(side):
    names=('study','checkpoint','collect');prior={k:sys.modules.get(k) for k in names};paths=list(sys.path)
    try:
        for name in names:sys.modules.pop(name,None)
        sys.path.insert(0,str(side));module=load('literal_audit_'+side.name,side/'collect.py')
    finally:
        sys.path[:]=paths
        for name,value in prior.items():
            if value is None:sys.modules.pop(name,None)
            else:sys.modules[name]=value
    c=module.source;assert c.study.ROOT==side and c.source.study is c.study
    return c


def mechanism(trace,source,answer):
    requests=[{'source_index':i,'text':v['content']} for i,v in enumerate(source)
              if v.get('role')=='user' and isinstance(v.get('content'),str)]
    observations=[];programs=[]
    for i,node in enumerate(trace.get('nodes') or []):
        message=node.get('message') or {};text=message.get('content')
        if message.get('role')=='tool' and isinstance(text,str):
            observations.append({'node':i,'text':text,'sha256':core.digest(text),
                'source_request_substring_indices':[r['source_index'] for r in requests if r['text'] and r['text'] in text]})
        for call in message.get('tool_calls') or []:
            if call.get('name')!='ipython':continue
            tree=None;code=None
            try:
                args=call.get('arguments');args=json.loads(args) if isinstance(args,str) else args
                code=args.get('code');tree=ast.parse(code)
            except (TypeError,ValueError,AttributeError,SyntaxError):pass
            constants=sorted({n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)}) if tree else []
            slots={n.targets[0].id:n.value.value for n in (tree.body if tree else [])
                   if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Constant)
                   and n.targets[0].id in ('request_text','ordinal','marker')}
            matches=[r['source_index'] for r in requests if any(v.strip().casefold()==r['text'].strip().casefold() for v in constants)]
            earlier=[o['node'] for o in observations if o['node']<i and set(matches)&set(o['source_request_substring_indices'])]
            programs.append({'node':i,'code':code,'code_sha256':core.digest(code),'ast_parseable':tree is not None,
                'ast_sha256':core.digest(ast.dump(tree)) if tree else None,'template_slots':slots,
                'literal_constant_matching_source_indices':matches,'earlier_request_observation_nodes':earlier,
                'print_call_candidate':bool(tree and any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='print' for n in ast.walk(tree))),
                'request_text_literal_source_indices':[r['source_index'] for r in requests if isinstance(slots.get('request_text'),str)
                    and r['text'].strip().casefold()==slots['request_text'].strip().casefold()]})
    final=trace.get('root_reply');diff=[]
    if isinstance(final,str):
        diff=[{'op':op,'gold_interval':[i,j],'final_interval':[k,l],'gold_text':answer[i:j],'final_text':final[k:l]}
              for op,i,j,k,l in difflib.SequenceMatcher(a=answer,b=final,autojunk=False).get_opcodes() if op!='equal']
    return {'programs':programs,'observations':observations,'source_user_requests':requests,
        'observed_before_literal_program_candidate':any(p['earlier_request_observation_nodes'] for p in programs),
        'inspection_adjudication':'UNREVIEWED','adjudication_rule':'Earlier substring plus a later matching constant is only a candidate. Inspect source-printing code, tool outcome, selector dataflow and actual retrieval; never infer use from correctness or string presence.',
        'full_gold_stdout':any(o['text'] in (answer,answer+'\n') for o in observations),
        'final_exact':final==answer if isinstance(final,str) else None,'final_diff':diff,
        'gold_sha256':core.digest(answer),'final_sha256':core.digest(final),'gold':answer,'final':final}


def audit_arm(side,tokenizer,renderer):
    c=bindings(side);s=c.study;out=side/'outputs/attempt-001';ready=core.read(s.READY)
    owner=core.read(out/'OWNER_TERMINAL.json');owner_run=core.read(out/'OWNER_RUN.json')
    assert owner_run['ready_identity']==ready['identity']
    if (out/'science/TERMINAL_STRIP_CONTRACT.json').exists():assert core.read(out/'science/TERMINAL_STRIP_CONTRACT.json')==c.hooks.qualify()
    if (out/'owned-service/BINDING.json').exists():assert core.read(out/'owned-service/BINDING.json')==c.checkpoint.binding('checkpoint32')
    plan=s.schedule('train');assert s.digest(plan)==ready['inputs']['schedule_sha256']
    gold=core.read(s.input_dir('train')/'HOST_GOLD.json');prefix=core.read(s.input_dir('train')/'PREFIXES.json')
    records={r['id']:r for r in s.records('train')};sources={k:core.read(Path(v['prompt_json_path'])) for k,v in records.items()}
    byid={r['id']:r for r in plan};native=[core.read(p) for p in sorted((out/'science/native-calls').glob('*-result.json'))]
    starts=[core.read(p) for p in sorted((out/'science/native-calls').glob('*-start.json'))];samples={};evidence=[]
    for p in sorted((out/'science/episodes').glob('*.json')):
        item=core.read(p);row=item['coordinate'];ident=row['id'];assert row==byid[ident] and ident not in samples
        sample=core.episode(item,native,gold[row['record_id']],prefix[ident]['token_ids'],None,c,tokenizer,renderer)
        traces=item['episode'].get('traces') or [];trace=traces[0] if len(traces)==1 else {}
        detail=mechanism(trace,sources[row['record_id']],gold[row['record_id']]['answer'])
        sample.update(full_gold_stdout=detail['full_gold_stdout'],observed_before_literal_program_candidate=detail['observed_before_literal_program_candidate'],
                      episode_path=str(p),episode_sha256=core.sha(p));samples[ident]=sample
        evidence.append({'coordinate':row,'episode_path':str(p),'episode_sha256':core.sha(p),**detail})
    saved=core.read(out/'science/RESULT.json') if (out/'science/RESULT.json').exists() else None
    available=sum(v['available'] for v in samples.values());exact=sum(v['binary_reward'] or 0 for v in samples.values())
    if saved:assert (saved['recorded'],saved['scientifically_available'],saved['raw_exact'])==(len(samples),available,exact)
    returned=[r for r in native if r['status']=='returned'];result_indices={r['index'] for r in native};start_indices={r['index'] for r in starts}
    assert len(result_indices)==len(native) and len(start_indices)==len(starts) and result_indices<=start_indices
    physical={'started':len(starts),'returned':len(returned),'errors':len(native)-len(returned),'start_only':len(starts)-len(native),
        'prompt_tokens_observed':sum(len(r['response']['tokens']['prompt_ids']) for r in returned),
        'completion_tokens_observed':sum(len(r['response']['tokens']['completion_ids']) for r in returned),
        'unreturned_cost_unknown_calls':len(starts)-len(returned),'subtotals_not_imputed_cost':True}
    return {'sidecar':str(side),'owner':owner,'owner_qualified':owner.get('complete') is True and owner.get('released') is True,
        'recorded':len(samples),'available':available,'raw_exact':exact,'unrecorded':32-len(samples),
        'recorded_unknown':len(samples)-available,'physical':physical,'plan':plan,'samples':samples,'records':records,'evidence':evidence}


def verify():
    ready=core.read(ROOT/'CPU_READY.json');assert ready['identity']==core.digest({k:v for k,v in ready.items() if k!='identity'})
    for p,w in ready['closure_sha256'].items():assert core.sha(p)==w,p
    assert core.sha(SIDE/'READY.json')==SIDE_SHA and core.sha(OLD_AUDIT)==OLD_SHA
    return ready


def build():
    out=SIDE/'outputs/attempt-001'
    if not (out/'OWNER_TERMINAL.json').exists():return {'status':'PENDING','one_check_no_polling':True},None
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    c=bindings(SIDE);tok=AutoTokenizer.from_pretrained(str(c.study.BASE),local_files_only=True);renderer=Qwen3Renderer(tok)
    old=audit_arm(CONTROL,tok,renderer);new=audit_arm(SIDE,tok,renderer)
    assert old['recorded']==old['available']==32 and old['raw_exact']==7
    assert old['records']==new['records']
    pairing=core.read(SIDE/'inputs/CONTROL_PAIRING.json')['pairs'];pairs=[]
    old_tasks=core.read(CONTROL/'inputs/train/tasks.json');new_tasks=core.read(SIDE/'inputs/train/tasks.json')
    for before,after,bind,oldtask,newtask in zip(old['plan'],new['plan'],pairing,old_tasks,new_tasks,strict=True):
        assert before['id']==bind['control_id'] and after['id']==bind['new_id']
        assert {k:v for k,v in before.items() if k not in ('id','study')}=={k:v for k,v in after.items() if k not in ('id','study')}
        assert newtask['prompt']==oldtask['prompt']+'\n\n'+c.study.INSPECT_RULE
        assert {k:v for k,v in oldtask.items() if k not in ('name','prompt')}=={k:v for k,v in newtask.items() if k not in ('name','prompt')}
        a=old['samples'][before['id']];b=new['samples'].get(after['id']);known=bool(a['available'] and b and b['available'])
        pairs.append({'record_id':after['record_id'],'repeat':after['repeat'],'seed':after['seed'],'old_id':before['id'],'new_id':after['id'],
            'old':a,'new':b,'paired_available':known,'win':bool(known and b['binary_reward']>a['binary_reward']),
            'loss':bool(known and b['binary_reward']<a['binary_reward']),
            'same_first_program':a['first_program_sha256']==b['first_program_sha256'] if b else None})
    assert len(pairs)==32 and [p['seed'] for p in pairs]==list(range(202609250000,202609250032))
    groups=[]
    for ident in old['records']:
        ps=sorted([p for p in pairs if p['record_id']==ident],key=lambda p:p['repeat'])
        groups.append({'record_id':ident,'old_vector':[p['old']['binary_reward'] for p in ps],
            'new_vector':[p['new']['binary_reward'] if p['new'] else None for p in ps],
            'old':core.group_summary([p['old'] for p in ps]),'new':core.group_summary([p['new'] for p in ps if p['new']]),'pairs':ps})
    def summary(arm):
        return {**{k:v for k,v in arm.items() if k in ('sidecar','owner','owner_qualified','recorded','available','raw_exact','unrecorded','recorded_unknown','physical')},
            'clean_target_stdout':sum(v['clean_target_stdout'] for v in arm['samples'].values()),
            'full_gold_stdout':sum(v['full_gold_stdout'] for v in arm['samples'].values()),
            'copy_differences':sum(v['failure_category']=='copy_difference' for v in arm['samples'].values()),
            'earlier_observation_candidates_not_confirmed_inspection':sum(v['observed_before_literal_program_candidate'] for v in arm['samples'].values()),
            'failure_categories':dict(Counter(v['failure_category'] for v in arm['samples'].values()))}
    report={'status':'TERMINAL_MATCHED_AUDIT','old':summary(old),'new':summary(new),'groups':groups,
        'paired_available':sum(p['paired_available'] for p in pairs),'wins':sum(p['win'] for p in pairs),'losses':sum(p['loss'] for p in pairs),
        'all32_retained':True,'actual_initial_prefix_condition':'Each arm checked against its own frozen expected prefix; change is intentional, not required identical.',
        'inspection_adjudication':'UNREVIEWED: all32 programs/observations in EVIDENCE.json require inert manual mechanism review',
        'source_sha256':dict(core.PINS),'GPU_calls':0,'optimizer_steps':0,
        'limits':'Eight exposed paired context units, four requested seeds each; not32 independent contexts. Same checkpoint/source/environment, intentionally different root wording and variable actual cost. No prompt sweep, raw metric rewrite, generated-code execution, or abstract recursion claim.'}
    return report,{'old':old['evidence'],'new':new['evidence']}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','check']);p.add_argument('--output',type=Path);args=p.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';ready=verify()
    if args.command=='verify':print({'identity':ready['identity']})
    else:
        report,evidence=build();report.update(analyzer_ready_sha256=core.sha(ROOT/'CPU_READY.json'),created_epoch=time.time())
        if args.output:
            assert not args.output.exists();core.write(args.output/'REPORT.json',report)
            if evidence:core.write(args.output/'EVIDENCE.json',evidence)
        print(json.dumps({k:v for k,v in report.items() if k not in ('groups','source_sha256')}))
