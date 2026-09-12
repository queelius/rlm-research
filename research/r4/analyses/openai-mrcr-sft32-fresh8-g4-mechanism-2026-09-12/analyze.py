"""Thin fresh8 binding of the proven G4 raw audit plus inert AST/source/copy comparisons."""
import ast
from collections import Counter
import difflib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
SIDE=STORE/'sidecars/openai-mrcr-procedural-sft32-fresh8-onpolicy-screen-v1';OUT=SIDE/'outputs/attempt-001'
CORE=ROOT.parent/'openai-mrcr-sft32-g4-mechanism-2026-09-12/analyze.py'
READY_SHA='c3a657addcf87f64b970fbe83de00d4e2fb1f83321139af2ed5d395e004f8061'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


core=load('fresh8_proven_core',CORE)


def bindings():
    previous_path=list(sys.path);names=('study','checkpoint','collect');previous={k:sys.modules.get(k) for k in names}
    try:
        for k in names:sys.modules.pop(k,None)
        sys.path.insert(0,str(SIDE));module=load('fresh8_audit_collector',SIDE/'collect.py')
    finally:
        sys.path[:]=previous_path
        for k,v in previous.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
    c=module.source;assert c.study.ROOT==SIDE and c.source.study is c.study
    return c


def code_slots(code):
    tree=ast.parse(code);values={}
    for node in tree.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            name=node.targets[0].id
            if name in ('request_text','ordinal','marker') and isinstance(node.value,ast.Constant):
                values[name]=node.value.value;node.value=ast.Constant(value='MASKED_'+name)
    return values,ast.dump(tree)


def detail(item,gold,record,templates,criteria):
    trace=item['episode']['traces'][0];codes=[]
    for n in trace['nodes']:
        for tc in n['message'].get('tool_calls',[]):
            if tc['name']=='ipython':codes.append(json.loads(tc['arguments'])['code'])
    slots,template=code_slots(codes[0]);messages=core.read(Path(record['prompt_json_path']))
    requested=Path(record['final_question_path']).read_text();core.PINS[record['final_question_path']]=core.sha(record['final_question_path'])
    genre_topic=requested.split('(1 indexed) ',1)[1].split('. Do not include',1)[0]
    kind,topic=genre_topic.split(' about ',1);truth=gold['answer'];final=trace['root_reply']
    observations=[n['message']['content'] for n in trace['nodes'] if n['message']['role']=='tool']
    indices=[i for i,m in enumerate(messages[:-1]) if m['role']=='user' and m['content'].strip().casefold()==slots['request_text'].casefold()]
    candidate_messages=[{'index':i,'content':m['content'],'following_role':messages[i+1]['role']} for i,m in enumerate(messages[:-1])
                        if i and m['role']=='user' and ' about '+topic in m['content']]
    changes=[{'op':tag,'gold_interval':[i,j],'final_interval':[k,l],'gold_text':truth[i:j],'final_text':final[k:l]}
             for tag,i,j,k,l in difflib.SequenceMatcher(a=truth,b=final,autojunk=False).get_opcodes() if tag!='equal']
    whitespace_only=''.join(truth.split())==''.join(final.split())
    return {'query':requested,'kind':kind,'topic':topic,'ordinal':slots['ordinal'],'first_program':codes[0],
        'all_programs':codes,'first_program_slots':slots,'teacher_exact_AST_applicable':False,
        'first_program_matches_teacher_AST_after_only_three_slot_masks':template in templates,
        'training_teacher_kind_count':sum(v['kind']==kind for v in criteria),
        'training_teacher_topic_count':sum(v['topic']==topic for v in criteria),
        'training_teacher_ordinal_count':sum(v['ordinal']==slots['ordinal'] for v in criteria),
        'literal_user_match_indices':indices,'same_topic_original_user_records':candidate_messages,
        'full_gold_stdout_first':observations[0] in (truth,truth+'\n'),
        'any_full_gold_stdout':any(o in (truth,truth+'\n') for o in observations),
        'final_equals_gold':final==truth,'final_whitespace_only_difference':final!=truth and whitespace_only,
        'gold_final_exact_diff':changes,'gold_sha256_canonical':core.digest(truth),'final_sha256_canonical':core.digest(final),
        'gold':truth,'final':final,'tool_observations':observations,'source_record':record,
        'interpretation_boundary':'AST slot matching and literal source inspection only; no generated program was executed. Genre/topic overlap is measured, not a causal familiarity label.'}


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (ROOT/'REPORT.json').exists()
    assert core.sha(SIDE/'READY.json')==READY_SHA
    ready=core.read(SIDE/'READY.json');owner=core.read(OUT/'OWNER_TERMINAL.json');assert owner['complete'] and owner['released']
    assert core.read(OUT/'OWNER_RUN.json')['ready_identity']==ready['identity']
    c=bindings();s=c.study;plan=s.schedule('train');assert s.digest(plan)==ready['inputs']['schedule_sha256']
    assert [v['seed'] for v in plan]==list(range(202609250000,202609250032))
    assert core.read(OUT/'science/TERMINAL_STRIP_CONTRACT.json')==c.hooks.qualify()
    baseline_binding=STORE/'sidecars/openai-mrcr-procedural-sft-continue32-eval-v1/outputs/held-checkpoint32-001/owned-service/BINDING.json'
    assert core.read(OUT/'owned-service/BINDING.json')==core.read(baseline_binding)
    corpus=core.read(STORE/'sidecars/openai-mrcr-procedural-sft-warmstart-v1/TEACHER_CORPUS_V2.json')
    criteria=[e['teacher']['criteria'] for e in corpus['episodes']];templates={code_slots(e['teacher']['authored_code'])[1] for e in corpus['episodes']}
    record_map={r['id']:r for r in s.records('train')};assert not set(record_map)&{e['episode_id'] for e in corpus['episodes']}
    assert not {r['source_row_sha256'] for r in record_map.values()}&{e['source']['source_row_sha256'] for e in corpus['episodes']}
    gold=core.read(s.input_dir('train')/'HOST_GOLD.json');prefix=core.read(s.input_dir('train')/'PREFIXES.json')
    native=[core.read(p) for p in sorted((OUT/'science/native-calls').glob('*-result.json'))]
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    tok=AutoTokenizer.from_pretrained(str(s.BASE),local_files_only=True);renderer=Qwen3Renderer(tok)
    planbyid={r['id']:r for r in plan};samples=[];evidence=[]
    for p in sorted((OUT/'science/episodes').glob('*.json')):
        item=core.read(p);row=item['coordinate'];assert row==planbyid[row['id']]
        sample=core.episode(item,native,gold[row['record_id']],prefix[row['id']]['token_ids'],None,c,tok,renderer)
        d=detail(item,gold[row['record_id']],record_map[row['record_id']],templates,criteria)
        sample.update({k:d[k] for k in ('kind','topic','ordinal','full_gold_stdout_first','any_full_gold_stdout','final_whitespace_only_difference','first_program_matches_teacher_AST_after_only_three_slot_masks','training_teacher_kind_count')})
        sample['teacher_exact_AST_applicable']=False;sample['episode_path']=str(p);samples.append(sample)
        evidence.append({'coordinate':row,'episode_path':str(p),'episode_sha256':core.sha(p),**d})
    assert len(samples)==len({v['coordinate']['id'] for v in samples})==32
    groups=[]
    for ident,r in record_map.items():
        values=sorted((v for v in samples if v['coordinate']['record_id']==ident),key=lambda v:v['coordinate']['repeat'])
        groups.append({'record_id':ident,'kind':values[0]['kind'],'topic':values[0]['topic'],**core.group_summary(values),'samples':values})
    saved=core.read(OUT/'science/RESULT.json');assert saved['raw_exact']==sum(v['binary_reward'] for v in samples)==7
    assert saved['scientifically_available']==sum(v['available'] for v in samples)==32
    old=core.read(ROOT.parent/'openai-mrcr-sft32-g4-mechanism-2026-09-12/MAIN_REPORT_001.json')
    for p in [CORE,Path(__file__),SIDE/'collect.py',SIDE/'study.py',SIDE/'checkpoint.py',s.PARENT/'collect.py']:
        core.PINS[str(p)]=core.sha(p)
    value={'schema':'fresh8-g4-independent-mechanism-v1','ready_sha256':READY_SHA,'owner':owner,'recorded':32,'available':32,'raw_exact':7,
       'groups':groups,'mixed_groups':sum(g['mixed_reward'] for g in groups),'all_correct_groups':sum(g['all_correct'] for g in groups),
       'full_gold_stdout_first':sum(v['full_gold_stdout_first'] for v in samples),'any_full_gold_stdout':sum(v['any_full_gold_stdout'] for v in samples),
       'first_AST_three_slot_template_matches':sum(v['first_program_matches_teacher_AST_after_only_three_slot_masks'] for v in samples),
       'failure_categories':dict(Counter(v['failure_category'] for v in samples)),
       'whitespace_only_final_failures':sum(v['final_whitespace_only_difference'] for v in samples),
       'teacher_kind_counts':dict(Counter(v['kind'] for v in criteria)),'teacher_ordinal_counts':dict(Counter(v['ordinal'] for v in criteria)),
       'fresh_row_hashes_disjoint_from_teacher_rows':True,'teacher_exact_AST_applicable':False,
       'physical':{'returned':sum(v['status']=='returned' for v in native),'errors':sum(v['status']!='returned' for v in native),
                   'root_actions':sum(v['root_actions'] for v in samples),'child_actions':sum(v['child_actions'] for v in samples)},
       'old8_diagnostic':{'raw_exact':old['raw_exact_available'],'available':old['available'],'mixed_groups':old['mixed_groups'],
                         'clean_stdout':sum(v['clean_target_stdout'] for g in old['groups'] for v in g['samples'])},
       'source_sha256':dict(core.PINS),'GPU_calls':0,'optimizer_steps':0,
       'limits':'Different8 context units and different seed block, not a paired checkpoint regression. Shared task/fewshot framing. Four draws/context not32 independent tasks. Old8 training examples; fresh8 rows absent from teacher corpus. No generated code executed and no training admission.'}
    core.write(ROOT/'REPORT.json',value);core.write(ROOT/'EVIDENCE.json',evidence)
    print(json.dumps({k:v for k,v in value.items() if k not in ('groups','source_sha256')}))
    print('REPORT_SHA',core.sha(ROOT/'REPORT.json'))


if __name__=='__main__':main()
