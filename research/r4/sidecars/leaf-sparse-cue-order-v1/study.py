"""Cadence4 cue-order96: exact exposed sources, neutral order wording, strict raw scoring."""
import ast
import hashlib
import importlib.util
import json
import random
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
PARENT=SIDE/'leaf-sparse-anchor-v1'
IDEAS=SIDE.parent/'ideas'
PINS={PARENT/'study.py':'2728361c0f6b12dc887d6e171cc1f12941380428ab983ad18403e7d47ea0faa9',
    PARENT/'SPEC.json':'1627f461a52811e68dfab15bd5a0ec1f173ef71accee493b50bc5fcb31c173c3',
    IDEAS/'2026-09-09-sparse-cue-order-design.md':'37843595c55e901130ece0d8944430fa2641d67232c1e5f2f1c681d0ed9a6c95',
    IDEAS/'2026-09-09-sparse-cue-order-plan.md':'66b604c540fe7a5ea907a9c060c44680344d4ba8d22f4f19ebd658d3dce4b231'}
for path,expected in PINS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('frozen source changed: '+str(path))
loader=importlib.util.spec_from_file_location('sparse_cue_private_source',PARENT/'study.py')
sparse=importlib.util.module_from_spec(loader);loader.loader.exec_module(sparse)
padding,anchor=sparse.padding,sparse.anchor
read,digest,file_hash,serialize,write_once=sparse.read,sparse.digest,sparse.file_hash,sparse.serialize,sparse.write_once
ordered_digest=sparse.ordered_digest
ALIAS,INPUT_MARKER=sparse.ALIAS,sparse.INPUT_MARKER
MASTER=981304001
SEEDS=[981304011,981304021]
ORDERS={'tag_first':('tag','label'),'label_first':('label','tag')}
CONDITIONS={'A':('matching','tag_first'),'B':('constant','tag_first'),
            'C':('matching','label_first'),'D':('constant','label_first')}
SEQUENCES=['ABDC','BCAD','CDBA','DACB']

def build_data():
    data=deepcopy(read(PARENT/'DATA.json'))
    data.update(master_seed=MASTER,sampling_seeds=SEEDS,
        reuse='Exact12 exposed sparse144 contexts/order; fresh sampling only, no old outcomes pooled')
    return data

def build_design(data):
    old=read(PARENT/'SPEC.json')['design']
    d={k:deepcopy(old[k]) for k in ['contract','labels','definitions','task_labels','task_definitions']}
    d.update(contexts=deepcopy(data['contexts']),model_alias=ALIAS,model_aliases={'old_sft':ALIAS},
        max_tokens=3072,max_concurrent_calls=4,call_timeout_seconds=120,wall_time_cap_seconds=600,
        plan=[],coordinates=[],batches=[])
    order=list(range(12));random.Random(MASTER).shuffle(order)
    for slot,index in enumerate(order):
        c=d['contexts'][index]
        repeats=[0,1] if slot%2==0 else [1,0]
        for repeat in repeats:
            sequence=SEQUENCES[(index+2*repeat)%4]
            for position,condition in enumerate(sequence):
                arm,field_order=CONDITIONS[condition]
                row=dict(dataset=c['dataset'],context_index=index,source_context_id=c['source_context_id'],
                    source_coordinate_id=c['source_coordinate_id'],weight='old_sft',source_prefix='q',number_namespace='disjoint',
                    arm=arm,condition=condition,field_order=field_order,cadence=4,anchor_positions=list(range(1,65,4)),
                    grammar='exact',seed=SEEDS[repeat],repeat=repeat,size=64,permutation=0,start=0,
                    sequence=sequence,context_dispatch_slot=slot,cell_order=position,unit_index=len(d['plan'])//4,
                    batch_id=len(d['batches']),dispatch_order=len(d['plan']))
                row['id']=row['coordinate_id']=digest([ROOT.name,row])
                d['plan'].append(row);d['coordinates'].append(deepcopy(row))
                d['batches'].append(dict(questions=[r['question'] for r in c['records']],
                    gold=dict(records=deepcopy(c['records']),labels=c['labels'],order=list(range(64)),
                        arm=arm,cadence=4,field_order=field_order)))
    dispatch_units(d)
    return d

def dispatch_units(design):
    plan=design['plan']
    if len(plan)%4:raise ValueError('incomplete dispatch quadruple')
    groups=[plan[i:i+4] for i in range(0,len(plan),4)]
    for group in groups:
        if len({(r['context_index'],r['seed']) for r in group})!=1 or {r['condition'] for r in group}!=set('ABCD'):
            raise ValueError('mixed or incomplete fixed quadruple')
        if ''.join(r['condition'] for r in group)!=group[0]['sequence']:
            raise ValueError('quadruple order changed')
    return groups

def make_request(design,row):
    body=sparse.make_request(design,row)
    text=body['messages'][1]['content']
    if text.count('the keys tag then label')!=1:raise ValueError('neutral instruction seam changed')
    body['messages'][1]['content']=text.replace('the keys tag then label','the keys tag and label')
    order=ORDERS[row['field_order']]
    for item in body['structured_outputs']['json']['prefixItems']:
        if item['type']=='object':
            props=item['properties'];item['properties']={k:props[k] for k in order};item['required']=list(order)
    return body

def synthetic_output(gold,label):
    raw=sparse.synthetic_output(gold,label)
    return [{k:item[k] for k in ORDERS[gold['field_order']]} if isinstance(item,dict) else item for item in raw]

def score_labels(content,gold):
    raw=None;n=len(gold['records']);order=ORDERS[gold['field_order']]
    try:
        raw=json.loads(content,object_pairs_hook=anchor.corr.strict_object,parse_constant=anchor.corr.reject_constant)
        if not isinstance(raw,list) or len(raw)!=n:raise ValueError('wrong_cardinality_or_representation')
        predicted=[]
        for i,(item,record) in enumerate(zip(raw,gold['records'],strict=True)):
            if i%4==0:
                if not isinstance(item,dict) or list(item)!=list(order):raise ValueError('wrong_assigned_anchor_order_or_properties')
                expected=record['id'] if gold['arm']=='matching' else 'p0000'
                if not isinstance(item['tag'],str) or item['tag']!=expected:raise ValueError('wrong_anchor_tag')
                label=item['label']
            else:label=item
            if not isinstance(label,str) or label not in gold['labels']:raise ValueError('noncanonical_label_or_nonanchor_type')
            predicted.append(label)
        return dict(parse_status='aligned',raw_array_length=n,schema_valid=True,records=n,aligned_records=n,
            predictions=predicted,strict_correct=sum(p==r['gold_label'] for p,r in zip(predicted,gold['records'],strict=True)),
            noncanonical_labels=0,output_positions=list(range(1,n+1)),input_positions=list(range(1,n+1)),
            assigned_field_order=gold['field_order'],assigned_order_conformant=True)
    except (TypeError,ValueError) as error:
        return dict(parse_status=str(error),raw_array_length=len(raw) if isinstance(raw,list) else None,schema_valid=False,
            records=n,aligned_records=0,predictions=[None]*n,strict_correct=0,noncanonical_labels=0,
            output_positions=[None]*n,input_positions=list(range(1,n+1)),assigned_field_order=gold['field_order'],assigned_order_conformant=False)

def score_coordinate(design,coordinate,records):
    # Reparse original response content; implementer projection never assumes stored scores are truth.
    fresh=[]
    for old in records:
        call=deepcopy(old)
        if call.get('score') is not None:
            raw=json.loads(call['raw_response_text']) if call.get('raw_response_text') else call['raw_response']
            message=raw['choices'][0]['message']
            call['score']=score_labels(None if message.get('tool_calls') else message.get('content'),design['batches'][coordinate['batch_id']]['gold'])
        fresh.append(call)
    value=sparse.score_coordinate(design,coordinate,fresh)
    observed=value['strict_correct_assignments'] is not None
    value['distance']=[dict(distance=d,planned=16,observed=16 if observed else 0,
        aligned=sum(r['aligned'] and r['distance_since_anchor']==d for r in value['records']),
        correct=sum(r['correct'] and r['distance_since_anchor']==d for r in value['records']) if observed else None) for d in range(4)]
    value['first_anchor']={}
    for name,positions in [('first',[1]),('later',list(range(5,65,4)))]:
        items=[r for r in value['records'] if r['input_position'] in positions]
        value['first_anchor'][name]=dict(planned=len(positions),observed=len(positions) if observed else 0,
            aligned=sum(r['aligned'] for r in items),correct=sum(r['correct'] for r in items) if observed else None)
    value['class_count_l1']=sum(abs(x) for x in value['class_count_errors'].values()) if value['class_count_errors'] is not None else None
    return value

def shift_interaction(values):
    if any(values.get(k) is None for k in 'ABCD'):return None
    a,b,c,d=[values[k] for k in 'ABCD']
    return ((c[1]-d[1])-(c[0]-d[0]))-((a[1]-b[1])-(a[0]-b[0]))

def summarize(design,records):
    by=defaultdict(list)
    for r in records:by[r['coordinate']['id']].append(r)
    coordinates=[score_coordinate(design,c,by[c['id']]) for c in design['coordinates']]
    cells=[]
    for task in ('trec','sst2','agnews'):
        for condition in 'ABCD':
            rows=[x for x in coordinates if (x['coordinate']['dataset'],x['coordinate']['condition'])==(task,condition)]
            obs=[x for x in rows if x['strict_correct_assignments'] is not None]
            aligned=[r for x in rows for r in x['records'] if r['aligned']]
            arm,order=CONDITIONS[condition]
            cells.append(dict(dataset=task,condition=condition,arm=arm,field_order=order,planned_calls=len(rows),observed_calls=len(obs),
                null_calls=len(rows)-len(obs),valid_calls=sum(x['fully_valid'] for x in rows),planned_assignments=64*len(rows),aligned_assignments=len(aligned),
                strict_correct=sum(x['strict_correct_assignments'] for x in obs),whole64_correct=sum(x['strict_full64_correct']==1 for x in obs),
                distance=[dict(distance=d,planned=16*len(rows),observed=16*len(obs),aligned=sum(r['distance_since_anchor']==d for r in aligned),
                    correct=sum(r['correct'] and r['distance_since_anchor']==d for r in aligned)) for d in range(4)],
                first_anchor={name:{key:sum(x['first_anchor'][name][key] or 0 for x in rows) for key in ('planned','observed','aligned','correct')} for name in ('first','later')},
                confusion=[dict(gold=g,prediction=p,count=n) for (g,p),n in sorted(Counter((r['gold'],r['prediction']) for r in aligned).items())],
                count_l1_sum=sum(x['class_count_l1'] for x in rows if x['class_count_l1'] is not None),count_l1_n=sum(x['class_count_l1'] is not None for x in rows),
                usage={k:sum(x['usage'][k] for x in rows) for k in rows[0]['usage']},missing_usage={k:sum(x['missing_usage'][k] for x in rows) for k in rows[0]['missing_usage']},
                call_seconds_sum=sum(x['call_wall_seconds_sum'] for x in rows),length_stops=sum(x['length_stops'] for x in rows)))
    groups=defaultdict(dict)
    for row in coordinates:
        c=row['coordinate'];groups[c['dataset'],c['context_index'],c['seed']][c['condition']]=row
    quads=[]
    for (task,context,seed),group in groups.items():
        rates={k:([d['correct']/16 for d in v['distance']] if v['strict_correct_assignments'] is not None else None) for k,v in group.items()}
        strict=shift_interaction(rates);valid=all(v['fully_valid'] for v in group.values())
        quads.append(dict(dataset=task,context_index=context,seed=seed,planned_calls=4,observed_calls=sum(v['strict_correct_assignments'] is not None for v in group.values()),
            jointly_valid=valid,strict_positive_shift_interaction=strict,joint_valid_interaction=strict if valid else None,
            condition_distance_rates=rates,matching_minus_constant_profile={order:[rates[m][d]-rates[c][d] for d in range(4)] if rates[m] is not None and rates[c] is not None else None for order,m,c in [('tag_first','A','B'),('label_first','C','D')]}))
    context_effects=[]
    for task,context in sorted({(x['dataset'],x['context_index']) for x in quads}):
        rows=[x for x in quads if (x['dataset'],x['context_index'])==(task,context)]
        values=[x['strict_positive_shift_interaction'] for x in rows]
        context_effects.append(dict(dataset=task,context_index=context,planned_seeds=2,complete_seeds=sum(x is not None for x in values),
            strict_interaction_mean=sum(values)/2 if len(values)==2 and all(x is not None for x in values) else None))
    tasks=[]
    for task in ('trec','sst2','agnews'):
        qs=[x for x in quads if x['dataset']==task];cs=[x for x in context_effects if x['dataset']==task]
        values=[x['strict_interaction_mean'] for x in cs]
        tasks.append(dict(dataset=task,planned_quadruples=8,complete_quadruples=sum(x['strict_positive_shift_interaction'] is not None for x in qs),joint_valid_quadruples=sum(x['jointly_valid'] for x in qs),
            planned_contexts=4,complete_contexts=sum(x is not None for x in values),strict_equal_context_mean=sum(values)/4 if all(x is not None for x in values) else None))
    return dict(coordinates=coordinates,cells=cells,quadruples=quads,context_effects=context_effects,task_primary=tasks,
        primary='[(M-C)d1-(M-C)d0]label-first minus tag-first; positive shift; tasks separate; two seeds averaged within four exposed contexts',
        audit_status='Implementer raw-derived projection, not independent outcome audit',
        limits='Observed invalid strict0; unavailable NULL; no repairs/retries/old pooling; first-anchor descriptive; not attention-mechanism or whole-RLM evidence')

# Only grouping changes in the pinned actual individual-row collector. Request/capture/finally unchanged.
COLLECTOR_PATH=anchor.corr.FIXED
COLLECTOR_SHA='9afd6c5d5219a6705c79839e99a87ca45e50c84fc7bdff197c97482f6cd8387a'
if file_hash(COLLECTOR_PATH)!=COLLECTOR_SHA:raise ValueError('qualified collector changed')
raw=COLLECTOR_PATH.read_text();node=next(n for n in ast.parse(raw).body if isinstance(n,ast.AsyncFunctionDef) and n.name=='collect_calls')
source=ast.get_source_segment(raw,node)
COLLECT_EDITS=[('pending = iter(design["plan"])','pending = iter(dispatch_units(design))',1),
    ('row = next(pending, None)','unit = next(pending, None)',1),('if row is None:','if unit is None:',1)]
for before,after,count in COLLECT_EDITS:
    if source.count(before)!=count:raise ValueError('grouping seam changed: '+before)
    source=source.replace(before,after)
start='            body = make_request(design, row)';end='\n    try:\n        async with asyncio.timeout'
if source.count(start)!=1 or source.count(end)!=1:raise ValueError('request body boundaries changed')
head,rest=source.split(start);body,tail=(start+rest).split(end)
source=head+'            for row in unit:\n                if stop.is_set():\n                    return\n'+''.join('    '+line+'\n' for line in body.splitlines())+end+tail
COLLECT_ADAPTED_SHA=hashlib.sha256(source.encode()).hexdigest()
anchor.corr.fixed.leaf.score_labels=score_labels
anchor.corr.fixed.leaf.write_once=write_once
scope={**anchor.corr.fixed.__dict__,'dispatch_units':dispatch_units,'make_request':make_request,'score_coordinate':score_coordinate}
exec(compile(source,str(COLLECTOR_PATH)+':quadruple-only-private','exec'),scope)
collect_calls=scope['collect_calls']
