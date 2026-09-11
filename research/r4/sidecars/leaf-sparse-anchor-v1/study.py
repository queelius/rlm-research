"""Fixed exposed source data; sparse mixed-output schema and strict labels."""
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
PARENT=SIDE/'leaf-identity-factorial-v1'
AG=SIDE/'leaf-identity-agnews-weight-v1'
PINS={PARENT/'study.py':'6294d813146cc75902cc5b61838046ed211ee8bc9002118a0bddd9dc9b06868e',
      PARENT/'SPEC.json':'150e2510a804042dc499fc1b9d8a195473d9f697c784a2bb929a803e96417792',
      AG/'SPEC.json':'052926cdb4b64cb38863241565bce8cf70f312fdf8922d383017075d3c1fc876'}
for path,expected in PINS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected: raise ValueError('frozen source changed: '+str(path))
loader=importlib.util.spec_from_file_location('sparse_private_factorial',PARENT/'study.py')
factorial=importlib.util.module_from_spec(loader);loader.loader.exec_module(factorial)
padding,anchor=factorial.padding,factorial.anchor
read,digest,file_hash,serialize,write_once=factorial.read,factorial.digest,factorial.file_hash,factorial.serialize,factorial.write_once
INPUT_MARKER=factorial.INPUT_MARKER
ALIAS='strict-rlm-qwen3-4b-role-sft-selected-v1'
MASTER=981296001
SEEDS=[981296011,981296021]
CADENCES=[1,4,16]
ARMS=['matching','constant']


def ordered_digest(value): return hashlib.sha256(serialize(value).encode()).hexdigest()


def build_data():
    contexts=[];source_specs={str(p):read(p) for p in (PARENT/'SPEC.json',AG/'SPEC.json')}
    for source_path,spec in source_specs.items():
        for c in sorted(spec['design']['contexts'],key=lambda x:x['index']):
            row=next(r for r in spec['design']['plan'] if r['context_index']==c['index'] and r['arm']=='meaningful_tag'
                and r['repeat']==r['permutation']==0 and r['source_prefix']=='q' and r['number_namespace']=='disjoint' and r['weight']=='old_sft')
            records=deepcopy(spec['design']['batches'][row['batch_id']]['gold']['records'])
            contexts.append(dict(index=len(contexts),source_context_index=c['index'],dataset=c['dataset'],
                source_context_id=c['source_context_id'],source_coordinate_id=row['id'],source_spec_path=source_path,
                source_spec_sha256=file_hash(source_path),records=records,base_request=deepcopy(spec['requests'][row['id']]),
                labels=spec['design']['task_labels'][c['dataset']]))
    if len(contexts)!=12 or Counter(c['dataset'] for c in contexts)!=dict(trec=4,sst2=4,agnews=4): raise ValueError('exact12 exposed context population')
    if any(len(c['records'])!=64 for c in contexts): raise ValueError('exact64 records')
    for task in ('trec','sst2','agnews'):
        groups=[r['group_id'] for c in contexts if c['dataset']==task for r in c['records']]
        if len(set(groups))!=256: raise ValueError('duplicate selected source groups')
    return dict(contexts=contexts,master_seed=MASTER,sampling_seeds=SEEDS,
        source_spec_sha256={str(p):file_hash(p) for p in (PARENT/'SPEC.json',AG/'SPEC.json')},
        source_provenance={'trec_sst':str(SIDE/'leaf-correspondence-anchor-transfer-v1/DATA.json'),
            'agnews':str(AG/'DATA.json'),'note':'Exact public-source provenance/unknown-license qualifications in frozen source closure'},
        exposure='All12 contexts previously exposed; first prior presentation only, no new source/holdout claim')


def build_design(data):
    prior=read(PARENT/'SPEC.json')['design']
    design={k:deepcopy(prior[k]) for k in ('contract','labels','definitions','task_labels','task_definitions')}
    ag=read(AG/'SPEC.json')['design']
    design['task_labels'].update(ag['task_labels']);design['task_definitions'].update(ag['task_definitions'])
    design.update(contexts=deepcopy(data['contexts']),model_alias=ALIAS,model_aliases={'old_sft':ALIAS},max_tokens=3072,
        max_concurrent_calls=4,call_timeout_seconds=120,wall_time_cap_seconds=900,plan=[],coordinates=[],batches=[])
    for c in design['contexts']:
        for repeat,seed in enumerate(SEEDS):
            shift=(c['index']+repeat)%3;cadences=CADENCES[shift:]+CADENCES[:shift]
            if (c['index']+repeat)%2: cadences.reverse()
            for cadence in cadences:
                arms=ARMS if (c['index']+repeat+CADENCES.index(cadence))%2==0 else list(reversed(ARMS))
                for pair_order,arm in enumerate(arms):
                    row=dict(dataset=c['dataset'],context_index=c['index'],source_context_id=c['source_context_id'],
                        source_coordinate_id=c['source_coordinate_id'],weight='old_sft',source_prefix='q',number_namespace='disjoint',
                        arm=arm,cadence=cadence,anchor_positions=list(range(1,65,cadence)),grammar='exact',seed=seed,repeat=repeat,
                        size=64,permutation=0,start=0,pair_order=pair_order,cell_order=len(design['plan'])%6,
                        batch_id=len(design['batches']),dispatch_order=len(design['plan']))
                    row['id']=row['coordinate_id']=digest([ROOT.name,row])
                    design['plan'].append(row);design['coordinates'].append(deepcopy(row))
                    design['batches'].append(dict(questions=[r['question'] for r in c['records']],
                        gold=dict(records=deepcopy(c['records']),labels=c['labels'],order=list(range(64)),arm=arm,cadence=cadence)))
    return design


def make_request(design,row):
    c=design['contexts'][row['context_index']];body=deepcopy(c['base_request']);body['seed']=row['seed']
    before,rest=body['messages'][1]['content'].split('Return only',1)
    rest=rest.split('\nAllowed labels:',1)[1]
    positions=', '.join(map(str,row['anchor_positions']))
    instruction=('Return only a JSON array in displayed input order, exactly one item per input record. '
        'Anchor positions are '+positions+'. At anchor positions emit an object with exactly the keys tag then label. ')
    instruction+=('Set tag to that record\'s source ID shown in the input. ' if row['arm']=='matching' else 'Set tag to the literal "p0000". ')
    instruction+=('Set label to that record\'s canonical label. At all other positions emit only the canonical label '
        'as a JSON string, not an object. Do not omit any input record.')
    body['messages'][1]['content']=before+instruction+'\nAllowed labels:'+rest
    items=[]
    for i,r in enumerate(c['records']):
        label={'type':'string','enum':c['labels']}
        if i%row['cadence']==0:
            items.append({'type':'object','properties':{'tag':{'type':'string','const':r['id'] if row['arm']=='matching' else 'p0000'},
                'label':label},'required':['tag','label'],'additionalProperties':False})
        else: items.append(label)
    body['structured_outputs']={'json':{'type':'array','prefixItems':items,'items':False,'minItems':64,'maxItems':64}}
    return body


def synthetic_output(gold,label):
    return [{'tag':r['id'] if gold['arm']=='matching' else 'p0000','label':label} if i%gold['cadence']==0 else label
            for i,r in enumerate(gold['records'])]


def score_labels(content,gold):
    n=len(gold['records']);raw=None;key_order=None
    try:
        raw=json.loads(content,object_pairs_hook=anchor.corr.strict_object,parse_constant=anchor.corr.reject_constant)
        if not isinstance(raw,list) or len(raw)!=n: raise ValueError('wrong_cardinality_or_representation')
        predictions=[];key_order=True
        for i,(item,record) in enumerate(zip(raw,gold['records'],strict=True)):
            if i%gold['cadence']==0:
                if not isinstance(item,dict): raise ValueError('anchor_not_object')
                if list(item)!=['tag','label']:
                    key_order=False;raise ValueError('wrong_anchor_key_order_or_properties')
                tag=record['id'] if gold['arm']=='matching' else 'p0000'
                if not isinstance(item['tag'],str) or item['tag']!=tag: raise ValueError('wrong_anchor_tag')
                label=item['label']
            else: label=item
            if not isinstance(label,str) or label not in gold['labels']: raise ValueError('noncanonical_label_or_nonanchor_type')
            predictions.append(label)
        return dict(parse_status='aligned',raw_array_length=n,schema_valid=True,records=n,aligned_records=n,
            predictions=predictions,strict_correct=sum(p==r['gold_label'] for p,r in zip(predictions,gold['records'],strict=True)),
            noncanonical_labels=0,output_positions=list(range(1,n+1)),input_positions=list(range(1,n+1)),anchor_key_order_valid=True)
    except (ValueError,TypeError) as error:
        return dict(parse_status=str(error),raw_array_length=len(raw) if isinstance(raw,list) else None,schema_valid=False,
            records=n,aligned_records=0,predictions=[None]*n,strict_correct=0,noncanonical_labels=0,
            output_positions=[None]*n,input_positions=list(range(1,n+1)),anchor_key_order_valid=key_order)


def score_coordinate(design,coordinate,records):
    value=padding.score_coordinate(design,coordinate,records)
    for item in value['records']:
        item['distance_since_anchor']=(item['input_position']-1)%coordinate['cadence']
    value['class_count_errors']=None
    if value['fully_valid']:
        gold=Counter(r['gold'] for r in value['records']);pred=Counter(r['prediction'] for r in value['records'])
        value['class_count_errors']={label:pred[label]-gold[label] for label in design['task_labels'][coordinate['dataset']]}
    return value


def summarize(design,records):
    by_id=defaultdict(list)
    for r in records: by_id[r['coordinate']['id']].append(r)
    coordinates=[score_coordinate(design,c,by_id[c['id']]) for c in design['coordinates']]
    cells=[];pairs=[];tradeoffs=[]
    for task in ('trec','sst2','agnews'):
        for cadence in CADENCES:
            for arm in ARMS:
                rows=[r for r in coordinates if (r['coordinate']['dataset'],r['coordinate']['cadence'],r['coordinate']['arm'])==(task,cadence,arm)]
                aligned=[i for r in rows for i in r['records'] if i['aligned']]
                observed=[r for r in rows if r['strict_correct_assignments'] is not None]
                cells.append(dict(dataset=task,cadence=cadence,arm=arm,planned_calls=len(rows),observed_calls=len(observed),
                    valid_calls=sum(r['fully_valid'] for r in rows),planned_assignments=64*len(rows),aligned_assignments=len(aligned),
                    strict_correct=sum(r['strict_correct_assignments'] for r in observed),whole64_correct=sum(r['strict_full64_correct']==1 for r in rows),
                    usage={k:sum(r['usage'][k] for r in rows) for k in rows[0]['usage']},
                    missing_usage={k:sum(r['missing_usage'][k] for r in rows) for k in rows[0]['missing_usage']},
                    length_stops=sum(r['length_stops'] for r in rows),call_seconds_sum=sum(r['call_wall_seconds_sum'] for r in rows),
                    distance=[dict(distance=d,aligned=sum(i['distance_since_anchor']==d for i in aligned),
                        correct=sum(i['distance_since_anchor']==d and i['correct'] for i in aligned)) for d in range(cadence)]))
    groups=defaultdict(dict)
    for r in coordinates:
        c=r['coordinate'];groups[c['dataset'],c['context_index'],c['seed']][c['cadence'],c['arm']]=r
    for (task,context,seed),group in groups.items():
        for cadence in CADENCES:
            m,c=group[cadence,'matching'],group[cadence,'constant']
            observed=m['strict_correct_assignments'] is not None and c['strict_correct_assignments'] is not None
            pairs.append(dict(dataset=task,context_index=context,seed=seed,cadence=cadence,
                jointly_valid=m['fully_valid'] and c['fully_valid'],matching_minus_constant_correct=
                    m['strict_correct_assignments']-c['strict_correct_assignments'] if observed else None))
        for cadence in (4,16):
            sparse,dense=group[cadence,'matching'],group[1,'matching']
            observed=sparse['strict_correct_assignments'] is not None and dense['strict_correct_assignments'] is not None
            usage_known=not sparse['missing_usage']['completion_tokens'] and not dense['missing_usage']['completion_tokens']
            tradeoffs.append(dict(dataset=task,context_index=context,seed=seed,cadence=cadence,
                sparse_minus_dense_correct=sparse['strict_correct_assignments']-dense['strict_correct_assignments'] if observed else None,
                sparse_minus_dense_output_tokens=sparse['usage']['completion_tokens']-dense['usage']['completion_tokens'] if usage_known else None))
    return dict(coordinates=coordinates,cells=cells,within_cadence_pairs=pairs,cross_cadence_tradeoffs=tradeoffs,
        primary='Matching-minus-constant within cadence, tasks separate; context groups with nested seeds',
        limits='Cross-cadence mixed representation and token-cost intervention; no hidden-state or whole-RLM claim; invalid observed0, infrastructure/unrun null; no repairs')


anchor.corr.fixed.make_request=make_request
anchor.corr.fixed.score_coordinate=score_coordinate
anchor.corr.fixed.leaf.score_labels=score_labels
anchor.corr.fixed.leaf.write_once=write_once
collect_calls=anchor.corr.fixed.collect_calls
