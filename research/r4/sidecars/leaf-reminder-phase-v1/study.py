"""Phase192: fixed records/prompt, schema-only phase and cue, within-record primary."""
import hashlib
import importlib.util
import json
import random
from collections import Counter,defaultdict
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;PARENT=SIDE/'leaf-sparse-anchor-v1';CUE=SIDE/'leaf-sparse-cue-order-v1'
PINS={CUE/'study.py':'f8b4a35523959b3cf7ddf1e3987607e2721503aa55e89bd96e64df205a02b697',
    SIDE.parent/'ideas/2026-09-09-reminder-phase-options.md':'6372272e4f07ef2d77c35a85caa1ca3290e83199e6ad72d7fd805cfa4e23061a',
    SIDE.parent/'ideas/2026-09-09-reminder-phase-main-approval.md':'ce45dd45d7b3bb1db42744d807e8991571352651f923c2c16dec6e857240a3c8'}
for p,h in PINS.items():
    if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('pinned source changed: '+str(p))
loader=importlib.util.spec_from_file_location('reminder_private_cue_source',CUE/'study.py');cue=importlib.util.module_from_spec(loader);loader.loader.exec_module(cue)
sparse,padding,anchor=cue.sparse,cue.padding,cue.anchor
read,digest,file_hash,serialize,write_once=cue.read,cue.digest,cue.file_hash,cue.serialize,cue.write_once
ordered_digest=cue.ordered_digest;ALIAS=cue.ALIAS;INPUT_MARKER=cue.INPUT_MARKER
MASTER=981310001;SEEDS=[981310011,981310021]
CONDITIONS={chr(65+p*2+a):(p,arm) for p in range(4) for a,arm in enumerate(('matching','constant'))}
SEQUENCES=[''.join(chr(65+(i+k)%8) for i in [0,1,7,2,6,3,5,4]) for k in range(8)]
INSTRUCTION=('Return only a JSON array in displayed input order, exactly one item per input record. '
    'Follow the required output format at each position. At object positions emit exactly the keys tag then label; '
    'the output format fixes the tag value. Set label to that displayed record\'s canonical label. '
    'At string positions emit only that displayed record\'s canonical label, not an object. Do not omit any input record.')

def is_anchor(index,phase):return index%4==phase
def distance(index,phase):return (index-phase)%4 if index>=phase else None

def build_data():
    data=deepcopy(read(PARENT/'DATA.json'));data.update(master_seed=MASTER,sampling_seeds=SEEDS,
        reuse='Exact12 exposed sparse contexts; no outcome selection/pooling; seed981308 proposal superseded by MAIN due active collision')
    return data

def build_design(data):
    old=read(PARENT/'SPEC.json')['design'];d={k:deepcopy(old[k]) for k in ('contract','labels','definitions','task_labels','task_definitions')}
    d.update(contexts=deepcopy(data['contexts']),model_alias=ALIAS,model_aliases={'old_sft':ALIAS},max_tokens=3072,
        max_concurrent_calls=4,call_timeout_seconds=120,wall_time_cap_seconds=600,plan=[],coordinates=[],batches=[])
    order=list(range(12));random.Random(MASTER).shuffle(order)
    for slot,index in enumerate(order):
        context=d['contexts'][index]
        for repeat in ([0,1] if slot%2==0 else [1,0]):
            sequence=SEQUENCES[(index*2+repeat)%8]
            for position,condition in enumerate(sequence):
                phase,arm=CONDITIONS[condition]
                row=dict(dataset=context['dataset'],context_index=index,source_context_id=context['source_context_id'],
                    source_coordinate_id=context['source_coordinate_id'],weight='old_sft',source_prefix='q',number_namespace='disjoint',
                    arm=arm,condition=condition,phase=phase,field_order='tag_first',cadence=4,anchor_positions=list(range(phase+1,65,4)),
                    grammar='exact',seed=SEEDS[repeat],repeat=repeat,size=64,permutation=0,start=0,sequence=sequence,
                    context_dispatch_slot=slot,cell_order=position,unit_index=len(d['plan'])//8,batch_id=len(d['batches']),dispatch_order=len(d['plan']))
                row['id']=row['coordinate_id']=digest([ROOT.name,row]);d['plan'].append(row);d['coordinates'].append(deepcopy(row))
                d['batches'].append({'questions':[r['question'] for r in context['records']],
                    'gold':{'records':deepcopy(context['records']),'labels':context['labels'],'order':list(range(64)),
                            'arm':arm,'cadence':4,'phase':phase,'field_order':'tag_first'}})
    dispatch_units(d);return d

def dispatch_units(design):
    rows=design['plan']
    if len(rows)%8:raise ValueError('incomplete eight-call unit')
    groups=[rows[i:i+8] for i in range(0,len(rows),8)]
    for group in groups:
        if len({(r['context_index'],r['seed']) for r in group})!=1 or {r['condition'] for r in group}!=set(CONDITIONS):raise ValueError('mixed/incomplete unit')
        if ''.join(r['condition'] for r in group)!=group[0]['sequence']:raise ValueError('fixed Williams order changed')
    return groups

def make_request(design,row):
    context=design['contexts'][row['context_index']];body=deepcopy(context['base_request']);body['seed']=row['seed']
    before,rest=body['messages'][1]['content'].split('Return only',1);rest=rest.split('\nAllowed labels:',1)[1]
    body['messages'][1]['content']=before+INSTRUCTION+'\nAllowed labels:'+rest
    items=[]
    for i,record in enumerate(context['records']):
        label={'type':'string','enum':context['labels']}
        items.append({'type':'object','properties':{'tag':{'type':'string','const':record['id'] if row['arm']=='matching' else 'p0000'},
            'label':label},'required':['tag','label'],'additionalProperties':False} if is_anchor(i,row['phase']) else label)
    body['structured_outputs']={'json':{'type':'array','prefixItems':items,'items':False,'minItems':64,'maxItems':64}}
    return body

def synthetic_output(gold,label):
    return [{'tag':r['id'] if gold['arm']=='matching' else 'p0000','label':label} if is_anchor(i,gold['phase']) else label for i,r in enumerate(gold['records'])]

def score_labels(content,gold):
    raw=None;n=len(gold['records'])
    try:
        raw=json.loads(content,object_pairs_hook=anchor.corr.strict_object,parse_constant=anchor.corr.reject_constant)
        if not isinstance(raw,list) or len(raw)!=n:raise ValueError('wrong_cardinality_or_representation')
        predictions=[]
        for i,(item,record) in enumerate(zip(raw,gold['records'],strict=True)):
            if is_anchor(i,gold['phase']):
                if not isinstance(item,dict) or list(item)!=['tag','label']:raise ValueError('wrong_anchor_order_or_properties')
                if item['tag']!=(record['id'] if gold['arm']=='matching' else 'p0000'):raise ValueError('wrong_anchor_tag')
                label=item['label']
            else:label=item
            if not isinstance(label,str) or label not in gold['labels']:raise ValueError('noncanonical_label_or_nonanchor_type')
            predictions.append(label)
        return dict(parse_status='aligned',raw_array_length=n,schema_valid=True,records=n,aligned_records=n,predictions=predictions,
            strict_correct=sum(p==r['gold_label'] for p,r in zip(predictions,gold['records'],strict=True)),noncanonical_labels=0,
            output_positions=list(range(1,n+1)),input_positions=list(range(1,n+1)),assigned_order_conformant=True)
    except (TypeError,ValueError) as error:
        return dict(parse_status=str(error),raw_array_length=len(raw) if isinstance(raw,list) else None,schema_valid=False,records=n,
            aligned_records=0,predictions=[None]*n,strict_correct=0,noncanonical_labels=0,output_positions=[None]*n,
            input_positions=list(range(1,n+1)),assigned_order_conformant=False)

def score_coordinate(design,coordinate,records):
    fresh=[]
    for original in records:
        call=deepcopy(original)
        if call.get('score') is not None:
            raw=json.loads(call['raw_response_text']) if call.get('raw_response_text') else call['raw_response'];message=raw['choices'][0]['message']
            call['score']=score_labels(None if message.get('tool_calls') else message.get('content'),design['batches'][coordinate['batch_id']]['gold'])
        fresh.append(call)
    result=padding.score_coordinate(design,coordinate,fresh)
    for record in result['records']:
        i=record['input_position']-1;record['distance_since_anchor']=distance(i,coordinate['phase']);record['primary_core']=i>=3
    if result['fully_valid']:
        gold=Counter(r['gold'] for r in result['records']);pred=Counter(r['prediction'] for r in result['records'])
        result['class_count_l1']=sum(abs(gold[k]-pred[k]) for k in design['task_labels'][coordinate['dataset']])
    else:result['class_count_l1']=None
    return result

def block_primary(values):
    if any(values.get((p,a)) is None for p in range(4) for a in ('matching','constant')):return None,None
    profile=[sum(values[((i-d)%4,'matching')][i]-values[((i-d)%4,'constant')][i] for i in range(3,64))/61 for d in range(4)]
    return profile[0]-profile[3],profile

def summarize(design,records):
    by=defaultdict(list)
    for r in records:by[r['coordinate']['id']].append(r)
    coordinates=[score_coordinate(design,r,by[r['id']]) for r in design['coordinates']];cells=[]
    for task in ('trec','sst2','agnews'):
        for phase in range(4):
            for arm in ('matching','constant'):
                rows=[r for r in coordinates if (r['coordinate']['dataset'],r['coordinate']['phase'],r['coordinate']['arm'])==(task,phase,arm)]
                obs=[r for r in rows if r['strict_correct_assignments'] is not None];aligned=[p for r in rows for p in r['records'] if p['aligned']]
                cells.append(dict(dataset=task,phase=phase,arm=arm,planned_calls=len(rows),observed_calls=len(obs),null_calls=len(rows)-len(obs),
                    valid_calls=sum(r['fully_valid'] for r in rows),planned_assignments=64*len(rows),aligned_assignments=len(aligned),
                    strict_correct=sum(r['strict_correct_assignments'] for r in obs),whole64_correct=sum(r['strict_full64_correct']==1 for r in obs),
                    usage={k:sum(r['usage'][k] for r in rows) for k in rows[0]['usage']},missing_usage={k:sum(r['missing_usage'][k] for r in rows) for k in rows[0]['missing_usage']},
                    count_l1_sum=sum(r['class_count_l1'] for r in rows if r['class_count_l1'] is not None),count_l1_n=sum(r['class_count_l1'] is not None for r in rows),
                    call_seconds_sum=sum(r['call_wall_seconds_sum'] for r in rows),length_stops=sum(r['length_stops'] for r in rows)))
    groups=defaultdict(dict)
    for row in coordinates:
        c=row['coordinate'];groups[c['dataset'],c['context_index'],c['seed']][c['phase'],c['arm']]=row
    blocks=[]
    for (task,context,seed),group in groups.items():
        values={key:[int(p['correct']) for p in row['records']] if row['strict_correct_assignments'] is not None else None for key,row in group.items()}
        primary,profile=block_primary(values);valid=all(row['fully_valid'] for row in group.values())
        blocks.append(dict(dataset=task,context_index=context,seed=seed,planned_calls=8,observed_calls=sum(v is not None for v in values.values()),
            jointly_valid=valid,primary=primary,matching_minus_constant_profile=profile,joint_valid_primary=primary if valid else None,
            core_records=61,boundary_records=[1,2,3]))
    contexts=[];tasks=[]
    for task,context in sorted({(r['dataset'],r['context_index']) for r in blocks}):
        rows=[r for r in blocks if (r['dataset'],r['context_index'])==(task,context)];values=[r['primary'] for r in rows]
        contexts.append(dict(dataset=task,context_index=context,planned_seeds=2,complete_seeds=sum(v is not None for v in values),
            mean=sum(values)/2 if len(values)==2 and all(v is not None for v in values) else None))
    for task in ('trec','sst2','agnews'):
        values=[r['mean'] for r in contexts if r['dataset']==task]
        tasks.append(dict(dataset=task,planned_contexts=4,complete_contexts=sum(v is not None for v in values),
            equal_context_mean=sum(values)/4 if len(values)==4 and all(v is not None for v in values) else None))
    return dict(coordinates=coordinates,cells=cells,blocks=blocks,context_effects=contexts,task_primary=tasks,
        primary='Within same61 records positions4..64: [(M-C)d0-(M-C)d3], two seeds then four equal contexts/task; positive direction',
        analysis_status='Implementer raw-derived projection; not independent outcome audit',
        limits='Exposed contexts; constrained action-space/prefix intervention; invalid0 versus unavailable NULL; no repairs or old pooling')

# Unchanged previously qualified grouped collector body. Only the dispatch_units callback now validates eight rows.
COLLECTOR_PATH=cue.COLLECTOR_PATH;COLLECTOR_SHA=cue.COLLECTOR_SHA;COLLECT_EDITS=cue.COLLECT_EDITS
COLLECT_ADAPTED_SHA=cue.COLLECT_ADAPTED_SHA
anchor.corr.fixed.leaf.score_labels=score_labels;anchor.corr.fixed.leaf.write_once=write_once
scope={**anchor.corr.fixed.__dict__,'dispatch_units':dispatch_units,'make_request':make_request,'score_coordinate':score_coordinate}
exec(compile(cue.source,str(COLLECTOR_PATH)+':eight-call-private-callback','exec'),scope);collect_calls=scope['collect_calls']
