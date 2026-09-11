"""144 fixed, exposed component calls on two released instruction checkpoints."""
import hashlib
import importlib.util
import itertools
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
SPARSE=SIDE/'leaf-sparse-anchor-v1'
CACHE=Path('/project/alex_phd/research-cache/models')
PINS={SPARSE/'study.py':'2728361c0f6b12dc887d6e171cc1f12941380428ab983ad18403e7d47ea0faa9',
      SPARSE/'DATA.json':'dc105fbb5a07703f79f09ac2af4394d5e529b77be64bce452882c36e5edcdb81',
      SPARSE/'SPEC.json':'1627f461a52811e68dfab15bd5a0ec1f173ef71accee493b50bc5fcb31c173c3'}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()


for path,expected in PINS.items():
    if sha(path)!=expected:raise ValueError('source changed: '+str(path))
loader=importlib.util.spec_from_file_location('qwen35_private_sparse',SPARSE/'study.py')
sparse=importlib.util.module_from_spec(loader);loader.loader.exec_module(sparse)
read,digest,serialize,write_once=sparse.read,sparse.digest,sparse.serialize,sparse.write_once
INPUT_MARKER=sparse.INPUT_MARKER
MASTER=981302001
SEEDS=[981302011,981302021]
ARMS=['plain','matching','constant']
MODELS={
    'qwen3':dict(alias='Qwen3-4B-Instruct-2507-no-research-adapter',path=str(CACHE/'Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554'),
        revision='cdbee75f17c01a7cc42f958dc650907174af0554',manifest_sha256='19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f'),
    'qwen35':dict(alias='Qwen3.5-4B-no-research-adapter',path=str(CACHE/'Qwen--Qwen3.5-4B--851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a'),
        revision='851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a',manifest_sha256='7c1cc9dc3dba23a31bff3ccbefbe23ee46b39cb5dd9b2675ac93c806d2c07e90')}


def build_data():
    data=read(SPARSE/'DATA.json')
    if Counter(c['dataset'] for c in data['contexts'])!=dict(trec=4,sst2=4,agnews=4):raise ValueError('source population')
    for task in ('trec','sst2','agnews'):
        groups=[r['group_id'] for c in data['contexts'] if c['dataset']==task for r in c['records']]
        if len(groups)!=256 or len(set(groups))!=256:raise ValueError('duplicate/incomplete source groups')
    return data


def build_design(data):
    d=dict(contexts=deepcopy(data['contexts']),plan=[],coordinates=[],batches=[],max_concurrent_calls=4,
        call_timeout_seconds=120,wall_time_cap_seconds=900,max_tokens=3072)
    orders=list(itertools.permutations(ARMS))
    for model in MODELS:
        for c in d['contexts']:
            for repeat,seed in enumerate(SEEDS):
                order=orders[(c['index']*2+repeat)%6]
                for arm in order:
                    r=dict(model=model,weight=model,dataset=c['dataset'],context_index=c['index'],arm=arm,
                        repeat=repeat,seed=seed,size=64,permutation=0,batch_id=len(d['batches']),dispatch_order=len(d['plan']))
                    r['id']=r['coordinate_id']=digest([ROOT.name,r])
                    d['plan'].append(r);d['coordinates'].append(deepcopy(r))
                    d['batches'].append(dict(gold=dict(records=deepcopy(c['records']),labels=c['labels'],arm=arm)))
    return d


def make_request(d,r):
    c=d['contexts'][r['context_index']];body=deepcopy(c['base_request']);arm=r['arm']
    before,rest=body['messages'][1]['content'].split('Return only',1);rest=rest.split('\nAllowed labels:',1)[1]
    instruction='Return only a JSON array in displayed input order, exactly one item per input record. '
    instruction+=('Emit only the canonical label as a JSON string at every position.' if arm=='plain' else
        'Emit an object with exactly the keys tag then label at every position. Set tag to '+
        ("that record's source ID shown in the input" if arm=='matching' else 'the literal "p0000"')+
        ". Set label to that record's canonical label.")
    body['messages'][1]['content']=before+instruction+' Do not omit any input record.\nAllowed labels:'+rest
    items=[{'type':'string','enum':c['labels']} if arm=='plain' else {'type':'object','properties':{
        'tag':{'type':'string','const':record['id'] if arm=='matching' else 'p0000'},
        'label':{'type':'string','enum':c['labels']}},'required':['tag','label'],'additionalProperties':False} for record in c['records']]
    body.update(model=MODELS[r['model']]['alias'],seed=r['seed'],temperature=.5,top_p=1,top_k=-1,min_p=0,
        repetition_penalty=1,presence_penalty=0,frequency_penalty=0,max_tokens=3072,
        chat_template_kwargs={'enable_thinking':False},structured_outputs={'json':{'type':'array','prefixItems':items,
        'items':False,'minItems':64,'maxItems':64}})
    return body


def synthetic(gold,label):
    return [label if gold['arm']=='plain' else {'tag':r['id'] if gold['arm']=='matching' else 'p0000','label':label} for r in gold['records']]


def score_labels(content,gold):
    n=len(gold['records']);raw=None;order=True
    try:
        raw=json.loads(content,object_pairs_hook=sparse.anchor.corr.strict_object,parse_constant=sparse.anchor.corr.reject_constant)
        if not isinstance(raw,list) or len(raw)!=n:raise ValueError('cardinality_or_array')
        predictions=[]
        for item,r in zip(raw,gold['records'],strict=True):
            if gold['arm']=='plain':label=item
            else:
                if not isinstance(item,dict) or set(item)!={'tag','label'}:raise ValueError('object_key_set')
                order=order and list(item)==['tag','label']
                if item['tag']!=(r['id'] if gold['arm']=='matching' else 'p0000'):raise ValueError('wrong_tag')
                label=item['label']
            if not isinstance(label,str) or label not in gold['labels']:raise ValueError('noncanonical_label')
            predictions.append(label)
        return dict(schema_valid=True,parse_status='aligned',aligned_records=n,predictions=predictions,
            strict_correct=sum(x==r['gold_label'] for x,r in zip(predictions,gold['records'],strict=True)),key_order_valid=order)
    except (ValueError,TypeError) as error:
        return dict(schema_valid=False,parse_status=str(error),aligned_records=0,predictions=[None]*n,strict_correct=0,key_order_valid=None)


def score_coordinate(d,c,records):
    if len(records)>1:raise ValueError('duplicate coordinate')
    r=records[0] if records else {};score=r.get('score');observed=score is not None
    expected=d.get('rendered_prompts',{}).get(c['id'],{})
    raw=r.get('raw_response') or {};ids=raw.get('prompt_token_ids');usage=raw.get('usage') or {}
    prompt_ok=isinstance(ids,list) and digest(ids)==expected.get('typed_token_ids_sha256')
    usage_ok=isinstance(ids,list) and len(ids)==usage.get('prompt_tokens')
    valid=bool(score and score['schema_valid']);gold=d['batches'][c['batch_id']]['gold']
    predictions=score['predictions'] if score else [None]*64
    gold_counts=Counter(x['gold_label'] for x in gold['records']);pred_counts=Counter(predictions) if valid else None
    return dict(coordinate=c,recorded=bool(records),observable=observed,fully_valid=valid,
        strict_correct_assignments=score['strict_correct'] if observed else None,
        strict_full64_correct=int(valid and score['strict_correct']==64) if observed else None,
        aligned_records=64 if valid else 0,key_order_valid=score.get('key_order_valid') if score else None,
        position_correct=[int(p==x['gold_label']) if valid else None for p,x in zip(predictions,gold['records'],strict=True)],
        class_count_l1=sum(abs(pred_counts[k]-gold_counts[k]) for k in gold['labels']) if valid else None,
        physical_prompt=dict(typed_template_equal=prompt_ok,reported_usage_length_equal=usage_ok,provider_ids_present=isinstance(ids,list)),
        unexpected_reasoning=bool((raw.get('choices') or [{}])[0].get('message',{}).get('reasoning') or (raw.get('choices') or [{}])[0].get('message',{}).get('reasoning_content')),
        usage=r.get('usage',{}),finish_reason=r.get('finish_reason'),error=r.get('error'),
        seconds=r.get('ended',0)-r.get('started',0) if records else None)


def summarize(d,records):
    by=defaultdict(list)
    for r in records:by[r['coordinate']['id']].append(r)
    rows=[score_coordinate(d,c,by[c['id']]) for c in d['coordinates']];cells=[];pairs=[]
    for model in dict.fromkeys(c['model'] for c in d['plan']):
        for task in ('trec','sst2','agnews'):
            for arm in ARMS:
                selected=[r for r in rows if (r['coordinate']['model'],r['coordinate']['dataset'],r['coordinate']['arm'])==(model,task,arm)]
                cells.append(dict(model=model,dataset=task,arm=arm,planned=len(selected),recorded=sum(r['recorded'] for r in selected),
                    observable=sum(r['observable'] for r in selected),valid=sum(r['fully_valid'] for r in selected),
                    correct=sum(r['strict_correct_assignments'] or 0 for r in selected),
                    whole64_correct=sum(r['strict_full64_correct'] or 0 for r in selected)))
    groups=defaultdict(dict)
    for r in rows:
        c=r['coordinate'];groups[c['model'],c['dataset'],c['context_index'],c['seed']][c['arm']]=r
    for key,g in groups.items():
        for control in ('constant','plain'):
            m,c=g['matching'],g[control];ok=m['observable'] and c['observable']
            pairs.append(dict(model=key[0],dataset=key[1],context=key[2],seed=key[3],contrast='matching-minus-'+control,
                correct_delta=m['strict_correct_assignments']-c['strict_correct_assignments'] if ok else None))
    return dict(coordinates=rows,cells=cells,pairs=pairs,unit='four exposed contexts per task; two nested seeds; no repair; invalid0 vs unavailable null')


sparse.anchor.corr.fixed.make_request=make_request
sparse.anchor.corr.fixed.score_coordinate=score_coordinate
sparse.anchor.corr.fixed.leaf.score_labels=score_labels
sparse.anchor.corr.fixed.leaf.write_once=write_once
collect_calls=sparse.anchor.corr.fixed.collect_calls
