"""Frozen top4-per-half candidates: fixed2+2 versus flexible4; no gold acquisition."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / 'musique-evidence-preservation-v1'
spec = importlib.util.spec_from_file_location('flex_original_study', PRIOR / 'study.py')
original = importlib.util.module_from_spec(spec); spec.loader.exec_module(original)
for name in ('read','sha','digest','write_x','load','aliases','base_owner','official','MODEL','MODEL_ALIAS','NATIVE','SYSTEM','FINAL','messages','decode','score_final','check_context','partition','SERVICE_ROOT'):
    globals()[name] = getattr(original, name)
INPUTS = ROOT / 'inputs'; READY = ROOT / 'CPU_READY.json'; ATTEMPT = ROOT / 'outputs/attempt-001'
OWNER_SECONDS, SCIENCE_SECONDS, EXTERNAL_SECONDS = 950, 700, 1050
PHYSICAL_CALLS = 60; ARMS = ('fixed', 'flexible'); NAMESPACE = 'musique-flexible-four-source-v1-20260912'
SELECT = 'Rank exactly four distinct original paragraph IDs from this source half by usefulness for answering the original question, most useful first. Return only JSON with exactly "paragraph_ids", a list of four integer IDs from the supplied paragraphs. Do not answer or summarize.'
PLAN = 'Choose exactly four distinct original paragraph IDs from the supplied candidate pool that together are most useful for answering the original question. You may choose any allocation across the two halves, including all four from one half. Return only JSON with exactly "paragraph_ids", a list of four candidate integer IDs. Do not answer or summarize. If selection_error is present and the candidate pool is empty, return {"paragraph_ids":[]}.'


def roles(): return ['select_left', 'select_right', 'plan', 'fixed', 'flexible']
def output_cap(role): return 1024 if role in ARMS else 128
def seed(index, role): return 202609230000 + 16*index + {'select_left':0,'select_right':1,'plan':2,'fixed':3,'flexible':3}[role]
def selected(): return read(INPUTS / 'PUBLIC_MANIFEST.json')['selected']
def schedule():
    result = []
    for index, item in enumerate(selected()):
        for role in roles():
            row = {'record_id':item['record_id'],'question_index':index,'role':role,'seed':seed(index,role),'max_tokens':output_cap(role),'temperature':.5}
            result.append({**row, 'call_id':digest([NAMESPACE,row])})
    return result


def selection(value, paragraphs):
    result = {'valid':False,'transport_valid':bool(value.get('transport_valid')),'model_error':False,
              'paragraph_ids':[],'paragraphs':[],'error':'selection_transport_unavailable'}
    if not result['transport_valid']: return result
    try:
        parsed = json.loads(value['text'], object_pairs_hook=official().strict_pairs)
        assert isinstance(parsed,dict) and set(parsed)=={'paragraph_ids'}
        ids = parsed['paragraph_ids']; allowed = {p['idx']:p for p in paragraphs}
        assert isinstance(ids,list) and len(ids)==4 and all(type(i) is int for i in ids)
        assert len(set(ids))==4 and all(i in allowed for i in ids)
        result.update(valid=True,paragraph_ids=ids,paragraphs=[allowed[i] for i in ids],error=None)
    except (ValueError,TypeError,AssertionError,KeyError): result.update(model_error=True,error='invalid_selection_schema_or_ids')
    return result


def selector_messages(public, half): return messages({'original_question':public['question'],'paragraphs':half},SELECT)
def shared_error(selections): return [{'stage':side,'error':v['error']} for side,v in zip(('select_left','select_right'),selections) if not v['valid']]
def candidates(selections):
    if shared_error(selections): return []
    return [{'half':side,'rank':rank+1,'paragraph':p} for side,v in zip(('left','right'),selections) for rank,p in enumerate(v['paragraphs'])]
def plan_messages(public, selections):
    return messages({'original_question':public['question'],'candidates':candidates(selections),'selection_error':shared_error(selections) or None},PLAN)
def branch(public, selections, planner, arm):
    error = shared_error(selections)
    if not error and arm=='flexible' and not planner['valid']: error=[{'stage':'plan','error':planner['error']}]
    paragraphs = [] if error else [p for v in selections for p in v['paragraphs'][:2]] if arm=='fixed' else planner['paragraphs']
    paragraphs = sorted(paragraphs,key=lambda p:p['idx'])
    return {'original_question':public['question'],'selected_ids':[p['idx'] for p in paragraphs],
            'selection_error':error or None,'evidence':paragraphs}


def request(prompt, role, sample_seed, n_paragraphs, tokenizer):
    rendered = tokenizer.apply_chat_template(prompt,tokenize=True,add_generation_prompt=True,enable_thinking=False)
    ids = rendered['input_ids'] if hasattr(rendered,'keys') else rendered
    check_context(ids,output_cap(role))
    sampling={'temperature':.5,'top_p':1.,'top_k':-1,'min_p':0.,'max_tokens':output_cap(role),'seed':sample_seed,'logprobs':1}
    if role in ARMS:
        schema={'type':'object','properties':{'answer':{'type':'string'},'support_idxs':{'type':'array','items':{'type':'integer','minimum':0,'maximum':n_paragraphs-1}}},'required':['answer','support_idxs'],'additionalProperties':False}
    else:
        payload=json.loads(prompt[1]['content'].rsplit('\n\n',1)[0])
        available=payload['paragraphs'] if role.startswith('select_') else [v['paragraph'] for v in payload['candidates']]
        count=4 if available else 0
        items={'type':'integer',**({'enum':[p['idx'] for p in available]} if available else {})}
        schema={'type':'object','properties':{'paragraph_ids':{'type':'array','minItems':count,'maxItems':count,'items':items}},'required':['paragraph_ids'],'additionalProperties':False}
    sampling['structured_outputs']={'json':schema}
    return {'model':MODEL_ALIAS,'token_ids':ids,'sampling_params':sampling,'cache_salt':'0'}


def verify():
    value=read(READY)
    assert value['identity']==digest({k:v for k,v in value.items() if k!='identity'})
    assert len(selected())==12 and len(schedule())==60 and digest(schedule())==value['schedule_sha256']
    for path,want in value['closure_sha256'].items(): assert sha(path)==want,path
    return value
