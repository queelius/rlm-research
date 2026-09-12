"""One quoted-relation extraction then unchanged final; frozen flexible four sources."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent;FLEX=ROOT.parent/'musique-flexible-four-source-v1'
spec=importlib.util.spec_from_file_location('relations_previous_study',FLEX/'study.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
for name in ('read','sha','digest','write_x','load','aliases','base_owner','official','MODEL','MODEL_ALIAS','NATIVE','SYSTEM','FINAL','messages','decode','score_final','check_context','SERVICE_ROOT','PRIOR'):
    globals()[name]=getattr(original,name)
INPUTS=ROOT/'inputs';READY=ROOT/'CPU_READY.json';ATTEMPT=ROOT/'outputs/attempt-001'
OWNER_SECONDS,SCIENCE_SECONDS,EXTERNAL_SECONDS=950,700,1050
NAMESPACE='musique-source-quoted-relations-v1-20260912'
EXTRACT='Extract up to four local subject-relation-object facts useful for answering the original question from ONLY these paragraphs. Preserve exactly which person, place or entity each fact concerns; do not transfer a fact merely because names or words match. Attach one exact nonempty quote from the cited original paragraph_text to each fact. Link facts through shared entities where supported. Report missing links separately. Do not answer the final question, use outside knowledge, or reject a useful local fact merely because it alone cannot answer the whole nested question. Return only JSON with relations (objects with subject, relation, object, paragraph_id, quote) and missing_links (strings).'


def roles():return ['extract','relations']
def selected():return read(INPUTS/'MANIFEST.json')['selected']
def output_cap(role):return 512 if role=='extract' else 1024
def seed(index,role):return 202609240000+16*index if role=='extract' else 202609230000+16*index+3
def schedule():
    result=[]
    for index,item in enumerate(selected()):
        for role in roles():
            row={'record_id':item['record_id'],'question_index':index,'role':role,'seed':seed(index,role),'max_tokens':output_cap(role),'temperature':.5}
            result.append({**row,'call_id':digest([NAMESPACE,row])})
    return result


def report(call,paragraphs):
    value={'valid':False,'model_error':False,'quote_substrings_verified':False,'relation_truth_verified':False,
           'data':{'relations':[],'missing_links':[]},'error':'extract_transport_unavailable'}
    if not call.get('transport_valid'):return value
    try:
        data=json.loads(call['text'],object_pairs_hook=official().strict_pairs)
        assert isinstance(data,dict) and set(data)=={'relations','missing_links'}
        assert isinstance(data['relations'],list) and len(data['relations'])<=4
        assert isinstance(data['missing_links'],list) and len(data['missing_links'])<=4
        assert all(isinstance(v,str) and v.strip() for v in data['missing_links'])
        originals={p['idx']:p['paragraph_text'] for p in paragraphs}
        for row in data['relations']:
            assert isinstance(row,dict) and set(row)=={'subject','relation','object','paragraph_id','quote'}
            assert all(isinstance(row[k],str) and row[k].strip() for k in ('subject','relation','object','quote'))
            assert type(row['paragraph_id']) is int and row['paragraph_id'] in originals
            assert row['quote'] in originals[row['paragraph_id']]
        value.update(valid=True,quote_substrings_verified=True,data=data,error=None)
    except (ValueError,TypeError,AssertionError,KeyError):value.update(model_error=True,error='invalid_report_schema_or_quote')
    return value


def extract_messages(payload):return messages({'original_question':payload['original_question'],'paragraphs':payload['evidence']},EXTRACT)
def final_messages(payload,value):
    relation_report={**value['data'],'error':value['error'],'quote_substrings_verified':value['quote_substrings_verified'],
                     'relation_truth_verified':False}
    return messages({**payload,'relation_report':relation_report},FINAL)


def request(prompt,role,sample_seed,n_paragraphs,tokenizer):
    rendered=tokenizer.apply_chat_template(prompt,tokenize=True,add_generation_prompt=True,enable_thinking=False)
    ids=rendered['input_ids'] if hasattr(rendered,'keys') else rendered;check_context(ids,output_cap(role))
    if role=='extract':
        paragraphs=json.loads(prompt[1]['content'].rsplit('\n\n',1)[0])['paragraphs']
        props={k:{'type':'string','minLength':1} for k in ('subject','relation','object','quote')}
        props['paragraph_id']={'type':'integer','enum':[p['idx'] for p in paragraphs]}
        row={'type':'object','properties':props,'required':list(props),'additionalProperties':False}
        schema={'type':'object','properties':{'relations':{'type':'array','maxItems':4,'items':row},
                'missing_links':{'type':'array','maxItems':4,'items':{'type':'string','minLength':1}}},
                'required':['relations','missing_links'],'additionalProperties':False}
    else:
        schema={'type':'object','properties':{'answer':{'type':'string'},'support_idxs':{'type':'array','items':{'type':'integer','minimum':0,'maximum':n_paragraphs-1}}},'required':['answer','support_idxs'],'additionalProperties':False}
    return {'model':MODEL_ALIAS,'token_ids':ids,'cache_salt':'0','sampling_params':{'temperature':.5,'top_p':1.,'top_k':-1,'min_p':0.,'max_tokens':output_cap(role),'seed':sample_seed,'logprobs':1,'structured_outputs':{'json':schema}}}


def check_binding(binding):assert digest(binding)==read(INPUTS/'MANIFEST.json')['baseline_binding_sha256_canonical']
def verify():
    value=read(READY);assert value['identity']==digest({k:v for k,v in value.items() if k!='identity'})
    assert len(selected())==12 and len(schedule())==24 and digest(schedule())==value['schedule_sha256']
    for path,want in value['closure_sha256'].items():assert sha(path)==want,path
    return value
