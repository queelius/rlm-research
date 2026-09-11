"""Deliberately shifted forced tags; positional labels remain the primary endpoint."""
import hashlib
import importlib.util
import itertools
import json
from collections import Counter,defaultdict
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;PARENT=SIDE/'leaf-sparse-anchor-v1'
IDEA=SIDE.parent/'ideas/2026-09-09-correspondence-to-rlm-next-options.md'
PINS={PARENT/'study.py':'2728361c0f6b12dc887d6e171cc1f12941380428ab983ad18403e7d47ea0faa9',
      PARENT/'DATA.json':'dc105fbb5a07703f79f09ac2af4394d5e529b77be64bce452882c36e5edcdb81',
      PARENT/'SPEC.json':'1627f461a52811e68dfab15bd5a0ec1f173ef71accee493b50bc5fcb31c173c3',
      IDEA:'4d4e6f3e89b5c0d438b3bcf9657efd0aa7a6a6db5cd7fb3dcc33dcf7f6e502a9'}
for path,want in PINS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest()!=want:raise ValueError('pinned source changed: '+str(path))
loader=importlib.util.spec_from_file_location('shifted_private_sparse',PARENT/'study.py')
sparse=importlib.util.module_from_spec(loader);loader.loader.exec_module(sparse)
padding,anchor=sparse.padding,sparse.anchor
read,digest,file_hash,serialize,write_once=sparse.read,sparse.digest,sparse.file_hash,sparse.serialize,sparse.write_once
ALIAS,INPUT_MARKER=sparse.ALIAS,sparse.INPUT_MARKER
MASTER=981327001;SEEDS=[981327011,981327021];ARMS=('matching','constant','shifted');SHIFT=17
INSTRUCTION=('Return only a JSON array in displayed input order, exactly one object per input record. '
    'Emit exactly the keys tag then label. The output format fixes the tag value. '
    'Set label to that displayed input record\'s canonical label, regardless of the forced tag value. '
    'Do not omit or reorder any input record.')

def ordered_digest(value):return hashlib.sha256(serialize(value).encode()).hexdigest()

def tags(records,arm):
    if arm=='matching':return [r['id'] for r in records]
    if arm=='constant':return ['p0000']*len(records)
    if arm=='shifted':return [records[(i+SHIFT)%len(records)]['id'] for i in range(len(records))]
    raise ValueError('unknown cue')

def build_data():
    data=deepcopy(read(PARENT/'DATA.json'));data.update(master_seed=MASTER,sampling_seeds=SEEDS,
        reuse='Exact12 exposed sparse contexts, no new selection; shifted schema contradicts positional instructions')
    return data

def build_design(data):
    old=read(PARENT/'SPEC.json')['design'];d={k:deepcopy(old[k]) for k in ('contract','labels','definitions','task_labels','task_definitions')}
    d.update(contexts=deepcopy(data['contexts']),model_alias=ALIAS,model_aliases={'old_sft':ALIAS},max_tokens=3072,
        max_concurrent_calls=4,call_timeout_seconds=120,wall_time_cap_seconds=600,plan=[],coordinates=[],batches=[])
    orders=list(itertools.permutations(ARMS))
    for context in d['contexts']:
        for repeat,seed in enumerate(SEEDS):
            for arm in orders[(context['index']*2+repeat)%6]:
                row=dict(dataset=context['dataset'],context_index=context['index'],source_context_id=context['source_context_id'],
                    source_coordinate_id=context['source_coordinate_id'],weight='old_sft',source_prefix='q',number_namespace='disjoint',
                    arm=arm,grammar='exact',seed=seed,repeat=repeat,size=64,permutation=0,start=0,
                    cadence=1,field_order='tag_first',shift=SHIFT if arm=='shifted' else None,
                    batch_id=len(d['batches']),dispatch_order=len(d['plan']),cell_order=len(d['plan'])%3)
                row['id']=row['coordinate_id']=digest([ROOT.name,row]);d['plan'].append(row);d['coordinates'].append(deepcopy(row))
                d['batches'].append({'questions':[r['question'] for r in context['records']],
                    'gold':{'records':deepcopy(context['records']),'labels':context['labels'],'order':list(range(64)),
                            'arm':arm,'cadence':1,'field_order':'tag_first'}})
    if len(d['plan'])!=72:raise ValueError('exact72 coordinates required')
    return d

def make_request(design,row):
    context=design['contexts'][row['context_index']];body=deepcopy(context['base_request']);body['seed']=row['seed']
    before,rest=body['messages'][1]['content'].split('Return only',1);rest=rest.split('\nAllowed labels:',1)[1]
    body['messages'][1]['content']=before+INSTRUCTION+'\nAllowed labels:'+rest
    items=[{'type':'object','properties':{'tag':{'type':'string','const':tag},'label':{'type':'string','enum':context['labels']}},
            'required':['tag','label'],'additionalProperties':False} for tag in tags(context['records'],row['arm'])]
    body['structured_outputs']={'json':{'type':'array','prefixItems':items,'items':False,'minItems':64,'maxItems':64}}
    return body

def score_labels(content,gold):
    raw=None;n=len(gold['records'])
    try:
        raw=json.loads(content,object_pairs_hook=anchor.corr.strict_object,parse_constant=anchor.corr.reject_constant)
        if not isinstance(raw,list) or len(raw)!=n:raise ValueError('wrong_cardinality_or_representation')
        predicted=[];expected=tags(gold['records'],gold['arm'])
        for item,tag in zip(raw,expected,strict=True):
            if not isinstance(item,dict) or list(item)!=['tag','label']:raise ValueError('wrong_object_order_or_properties')
            if item['tag']!=tag:raise ValueError('wrong_forced_tag')
            if not isinstance(item['label'],str) or item['label'] not in gold['labels']:raise ValueError('noncanonical_label')
            predicted.append(item['label'])
        correct=sum(p==r['gold_label'] for p,r in zip(predicted,gold['records'],strict=True))
        by_id={r['id']:r['gold_label'] for r in gold['records']}
        named=sum(p==by_id[tag] for p,tag in zip(predicted,expected)) if gold['arm']!='constant' else None
        return dict(parse_status='aligned',raw_array_length=n,schema_valid=True,records=n,aligned_records=n,predictions=predicted,
            strict_correct=correct,noncanonical_labels=0,output_positions=list(range(1,n+1)),input_positions=list(range(1,n+1)),
            named_record_correct=named,named_minus_displayed=named-correct if named is not None else None,
            diagnostic_replaces_primary=False,assigned_order_conformant=True)
    except (ValueError,TypeError) as error:
        return dict(parse_status=str(error),raw_array_length=len(raw) if isinstance(raw,list) else None,schema_valid=False,records=n,
            aligned_records=0,predictions=[None]*n,strict_correct=0,noncanonical_labels=0,output_positions=[None]*n,
            input_positions=list(range(1,n+1)),named_record_correct=None,named_minus_displayed=None,
            diagnostic_replaces_primary=False,assigned_order_conformant=False)

def score_coordinate(design,coordinate,records):
    value=padding.score_coordinate(design,coordinate,records)
    score=records[0].get('score') if records else None
    value['named_record_correct']=score['named_record_correct'] if score and value['fully_valid'] else None
    value['named_minus_displayed']=score['named_minus_displayed'] if score and value['fully_valid'] else None
    if value['fully_valid']:
        truth=Counter(r['gold'] for r in value['records']);pred=Counter(r['prediction'] for r in value['records'])
        value['class_count_l1']=sum(abs(truth[k]-pred[k]) for k in design['task_labels'][coordinate['dataset']])
    else:value['class_count_l1']=None
    return value

def summarize(design,records):
    by=defaultdict(list)
    for record in records:by[record['coordinate']['id']].append(record)
    values=[score_coordinate(design,c,by[c['id']]) for c in design['coordinates']];cells=[];pairs=[];contexts=[]
    for task in ('trec','sst2','agnews'):
        for arm in ARMS:
            rows=[v for v in values if (v['coordinate']['dataset'],v['coordinate']['arm'])==(task,arm)]
            observed=[v for v in rows if v['strict_correct_assignments'] is not None]
            cells.append(dict(dataset=task,arm=arm,planned_calls=len(rows),observed_calls=len(observed),null_calls=len(rows)-len(observed),
                valid_calls=sum(v['fully_valid'] for v in rows),strict_correct=sum(v['strict_correct_assignments'] for v in observed),
                planned_assignments=64*len(rows),whole64_correct=sum(v['strict_full64_correct']==1 for v in rows),
                named_record_correct_sum=sum(v['named_record_correct'] or 0 for v in rows),named_record_diagnostic_calls=sum(v['named_record_correct'] is not None for v in rows),
                count_l1_sum=sum(v['class_count_l1'] or 0 for v in rows),count_l1_calls=sum(v['class_count_l1'] is not None for v in rows),
                usage={k:sum(v['usage'][k] for v in rows) for k in rows[0]['usage']},
                missing_usage={k:sum(v['missing_usage'][k] for v in rows) for k in rows[0]['missing_usage']},
                call_seconds_sum=sum(v['call_wall_seconds_sum'] for v in rows)))
    by_pair=defaultdict(dict)
    for v in values:
        c=v['coordinate'];by_pair[c['dataset'],c['context_index'],c['seed']][c['arm']]=v
    for (task,context,seed),arms in by_pair.items():
        for control in ('constant','shifted'):
            left,right=arms['matching'],arms[control];x,y=left['strict_correct_assignments'],right['strict_correct_assignments']
            pairs.append({'dataset':task,'context_index':context,'seed':seed,'contrast':'matching-minus-'+control,
                'difference':x-y if x is not None and y is not None else None,
                'jointly_valid':left['fully_valid'] and right['fully_valid']})
    for task,context,contrast in sorted({(p['dataset'],p['context_index'],p['contrast']) for p in pairs}):
        numbers=[p['difference'] for p in pairs if (p['dataset'],p['context_index'],p['contrast'])==(task,context,contrast)]
        contexts.append({'dataset':task,'context_index':context,'contrast':contrast,'two_seed_mean':sum(numbers)/2 if len(numbers)==2 and all(v is not None for v in numbers) else None})
    return {'coordinates':values,'cells':cells,'pairs':pairs,'context_effects':contexts,
        'primary':'Displayed-position strict correctness, matching-minus-constant/shifted; tasks and four context clusters separate',
        'diagnostic':'Named-record score and named-minus-displayed only on valid matching/shifted arrays; never repairs primary',
        'analysis_status':'Implementer projection, not independent audit','limits':'Contradictory cue; exposed records; no equal realized output-token or attention/RLM claim'}

anchor.corr.fixed.make_request=make_request;anchor.corr.fixed.score_coordinate=score_coordinate
anchor.corr.fixed.leaf.score_labels=score_labels;anchor.corr.fixed.leaf.write_once=write_once
collect_calls=anchor.corr.fixed.collect_calls
