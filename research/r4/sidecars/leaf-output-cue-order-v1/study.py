"""Supplied source-cue timing: frozen inputs, actual object order, no answer repair."""
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
PARENT=SIDE/'leaf-identity-factorial-v1'
IDEA=SIDE.parent/'ideas/2026-09-09-output-cue-order-design.md'
FEASIBILITY=IDEA.with_name('2026-09-09-output-cue-order-feasibility.json')
FEASIBILITY_SOURCE=FEASIBILITY.with_suffix('.py')
DECISION=SIDE.parent/'operations/2026-09-09-continuous-allocation/OUTPUT_CUE_ORDER_CPU_DECISION.md'
PINS={PARENT/'study.py':'6294d813146cc75902cc5b61838046ed211ee8bc9002118a0bddd9dc9b06868e',
      PARENT/'SPEC.json':'150e2510a804042dc499fc1b9d8a195473d9f697c784a2bb929a803e96417792',
      IDEA:'86271569364b54a2392739f6d461b55495b413149d718c622842f191a6023581',
      FEASIBILITY:'a8fad088659314433e562e41ed3713b6a0be9c6be7b9ae088a6a67e9aa90afa6',
      FEASIBILITY_SOURCE:'890738a9d5081453898f839422d9f97684f603fdf2d348635c06f8b4751f1668',
      DECISION:'386e59cfc42e2384e1c10851b5ad98de6db757d2aacc5a85ecabc52c105e3626'}
for path,sha in PINS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest()!=sha: raise ValueError('pinned source changed: '+str(path))
loader=importlib.util.spec_from_file_location('cue_order_private_factorial',PARENT/'study.py')
factorial=importlib.util.module_from_spec(loader);loader.loader.exec_module(factorial)
counter,padding,anchor=factorial.counter,factorial.padding,factorial.anchor
read,digest,file_hash,serialize,write_once=factorial.read,factorial.digest,factorial.file_hash,factorial.serialize,factorial.write_once
ALIAS,INPUT_MARKER=factorial.ALIAS,factorial.INPUT_MARKER
ARMS=['meaningful_tag','ordinal_tag','constant_tag']
ORDERS={'tag_first':('tag','label'),'label_first':('label','tag')}
MASTER=981282001
SEEDS=[981282011,981282021]
expected_tags=factorial.expected_tags
PRIOR=read(PARENT/'SPEC.json')


def ordered_digest(value):
    return hashlib.sha256(serialize(value).encode()).hexdigest()


def build_data():
    contexts=[]
    for dataset in ['trec','sst2']:
        contexts.extend(sorted((c for c in PRIOR['design']['contexts'] if c['dataset']==dataset),key=lambda c:c['index'])[:2])
    if len(contexts)!=4: raise ValueError('four rule-selected contexts unavailable')
    return {'contexts':deepcopy(contexts),'source_path':str(PARENT/'SPEC.json'),'source_sha256':PINS[PARENT/'SPEC.json'],
        'selection':'Lowest two original context indexes per task, TREC then SST; first prior presentation, disjoint q IDs',
        'freshness':'Exposed explanatory contexts; no new-data replication; original source provenance inherited',
        'sampling_seeds':SEEDS,'master_seed':MASTER}


def build_design(data):
    previous=PRIOR['design']
    d={k:deepcopy(previous[k]) for k in ['contract','labels','definitions','task_labels','task_definitions']}
    d.update(contexts=deepcopy(data['contexts']),model_alias=ALIAS,model_aliases={'old_sft':ALIAS},
        max_tokens=3072,max_concurrent_calls=4,call_timeout_seconds=120,wall_time_cap_seconds=600,
        plan=[],coordinates=[],batches=[])
    for local,c in enumerate(d['contexts']):
        for repeat,seed in enumerate(SEEDS):
            shift=(local+repeat)%3
            arms=ARMS[shift:]+ARMS[:shift]
            if (local+repeat)%2: arms=list(reversed(arms))
            for arm in arms:
                old=next(r for r in previous['plan'] if r['context_index']==c['index'] and r['arm']==arm
                    and r['repeat']==r['permutation']==0 and r['source_prefix']=='q' and r['number_namespace']=='disjoint')
                orders=list(ORDERS)
                if (local+repeat+ARMS.index(arm))%2: orders.reverse()
                for order in orders:
                    row={**deepcopy(old),'seed':seed,'repeat':repeat,'field_order':order,'local_context_index':local,
                        'source_coordinate_id':old['id'],'batch_id':len(d['batches']),
                        'cell_order':len(d['plan'])%6,'dispatch_order':len(d['plan'])}
                    row.pop('id');row.pop('coordinate_id')
                    row['id']=row['coordinate_id']=digest([ROOT.name,row])
                    batch=deepcopy(previous['batches'][old['batch_id']]);batch['gold']['field_order']=order
                    d['plan'].append(row);d['coordinates'].append(deepcopy(row));d['batches'].append(batch)
    return d


def make_request(design,row):
    body=deepcopy(PRIOR['requests'][row['source_coordinate_id']])
    body['seed']=row['seed']
    text=body['messages'][1]['content']
    if text.count('the keys tag then label')!=1: raise ValueError('instruction seam changed')
    body['messages'][1]['content']=text.replace('the keys tag then label','the keys tag and label')
    order=ORDERS[row['field_order']]
    for item in body['structured_outputs']['json']['prefixItems']:
        props=item['properties'];item['properties']={key:props[key] for key in order};item['required']=list(order)
    return body


def score_labels(content,gold):
    # Strict duplicate-rejecting raw parse comes before any semantic scorer.
    raw=None;raw_orders=None
    try:
        raw=json.loads(content,object_pairs_hook=anchor.corr.strict_object,parse_constant=anchor.corr.reject_constant)
        if not isinstance(raw,list) or len(raw)!=len(gold['records']): raise ValueError('wrong_cardinality_or_representation')
        raw_orders=dict(Counter(','.join(item) if isinstance(item,dict) else '<non-object>' for item in raw))
        for item in raw:
            if not isinstance(item,dict) or set(item)!={'tag','label'}: raise ValueError('wrong_object_shape')
            if list(item)!=list(ORDERS[gold['field_order']]): raise ValueError('wrong_physical_key_order')
    except (TypeError,ValueError) as error:
        n=len(gold['records'])
        score={'parse_status':str(error),'raw_array_length':len(raw) if isinstance(raw,list) else None,
            'schema_valid':False,'records':n,'aligned_records':0,'predictions':[None]*n,'strict_correct':0,
            'noncanonical_labels':0,'output_positions':[None]*n,'input_positions':list(range(1,n+1))}
    else:
        tags=expected_tags(gold['records'],gold['arm'],gold['source_prefix'])
        adapted={**gold,'arm':'meaningful_tag','records':[{**r,'id':tag} for r,tag in zip(gold['records'],tags,strict=True)]}
        # Frozen scorer checks tag and label; receives original unchanged content.
        score=padding.score_labels(content,adapted)
    score['assigned_field_order']=gold['field_order'];score['raw_object_key_orders']=raw_orders
    diagnostic={'positions':max(0,len(gold['records'])-1),'previous_correct':None,'first_item_correct':None,
        'first_item_previous_correct':None,'multiset_chance_expected_matches':None,'primary_replaced':False,
        'caution':'Repeated labels make agreement non-identifying; chance fixes prediction and previous-gold multisets, not independent observations'}
    if score['schema_valid']:
        predicted=score['predictions'];labels=[r['gold_label'] for r in gold['records']]
        pc,gc=Counter(predicted[1:]),Counter(labels[:-1]);n=len(predicted)-1
        diagnostic.update(previous_correct=sum(a==b for a,b in zip(predicted[1:],labels[:-1],strict=True)),
            first_item_correct=int(predicted[0]==labels[0]),
            multiset_chance_expected_matches=sum(pc[k]*gc[k] for k in pc)/n if n else None)
    score['previous_record_diagnostic']=diagnostic
    return score


def score_coordinate(design,coordinate,records):
    value=counter.score_coordinate(design,coordinate,records)
    value['class_count_l1']=sum(abs(v) for v in value['class_count_errors'].values()) if value['class_count_errors'] is not None else None
    value['previous_record_diagnostic']=records[0]['score']['previous_record_diagnostic'] if records and records[0].get('score') else None
    value['raw_object_key_orders']=records[0]['score']['raw_object_key_orders'] if records and records[0].get('score') else None
    return value


def summarize(design,records):
    by_id=defaultdict(list)
    for r in records: by_id[r['coordinate']['id']].append(r)
    coordinates=[score_coordinate(design,c,by_id[c['id']]) for c in design['coordinates']]
    fields=['dataset','arm','field_order'];cells=[]
    for key in sorted({tuple(c['coordinate'][f] for f in fields) for c in coordinates}):
        selected=[c for c in coordinates if tuple(c['coordinate'][f] for f in fields)==key]
        items=[i for c in selected for i in c['records'] if i['aligned']]
        cells.append({**dict(zip(fields,key)),'planned_calls':len(selected),'observable_calls':sum(c['strict_correct_assignments'] is not None for c in selected),
            'recorded_calls':sum(c['complete'] for c in selected),'valid_calls':sum(c['fully_valid'] for c in selected),
            'infrastructure_errors':sum(c['infrastructure_errors'] for c in selected),
            'planned_assignments':64*len(selected),'aligned_assignments':len(items),'canonical_correct':sum(i['correct'] for i in items),
            'complete_batch_correct':sum(c['strict_full64_correct']==1 for c in selected),
            'per_call_class_count_l1':[{'coordinate_id':c['coordinate']['id'],'l1':c['class_count_l1']} for c in selected],
            'usage':{k:sum(c['usage'][k] for c in selected) for k in ['logical_input_tokens','cached_input_tokens','uncached_input_tokens','completion_tokens']},
            'missing_usage':{k:sum(c['missing_usage'][k] for c in selected) for k in ['logical_input_tokens','cached_input_tokens','uncached_input_tokens','completion_tokens']},
            'length_stops':sum(c['length_stops'] for c in selected),'call_wall_seconds_sum':sum(c['call_wall_seconds_sum'] for c in selected)})
    groups=defaultdict(dict)
    for v in coordinates:
        c=v['coordinate'];groups[c['dataset'],c['context_index'],c['repeat'],c['field_order']][c['arm']]=v
    pairs=[];interactions=defaultdict(dict)
    for key,arms in groups.items():
        for left,right in [('ordinal_tag','meaningful_tag'),('constant_tag','meaningful_tag'),('constant_tag','ordinal_tag')]:
            if left not in arms or right not in arms: continue
            a,b=arms[left],arms[right]
            observed=a['strict_correct_assignments'] is not None and b['strict_correct_assignments'] is not None
            valid=a['fully_valid'] and b['fully_valid']
            row={**dict(zip(['dataset','context_index','repeat','field_order'],key)),'contrast':right+'_minus_'+left,
                'both_observed':observed,'jointly_valid':valid,
                'strict_difference':b['strict_correct_assignments']-a['strict_correct_assignments'] if observed else None,
                'semantic_difference':b['semantic_correct_among_aligned']-a['semantic_correct_among_aligned'] if valid else None}
            pairs.append(row)
            if left=='ordinal_tag': interactions[key[:3]][key[3]]=row
    interaction_rows=[]
    for key,orders in interactions.items():
        a,b=orders.get('tag_first',{}).get('strict_difference'),orders.get('label_first',{}).get('strict_difference')
        interaction_rows.append({**dict(zip(['dataset','context_index','repeat'],key)),
            'tag_first_minus_label_first_meaningful_minus_ordinal':a-b if a is not None and b is not None else None})
    return {'coordinates':coordinates,'cells':cells,'paired_context_effects':pairs,'order_interactions':interaction_rows,
        'primary':'Displayed-record meaningful-minus-ordinal within order, and tag-first minus label-first interaction; tasks separate',
        'inference_unit':'Two exposed context clusters per task; seeds nested, not3072 independent labels; no whole-RLM claim',
        'failure_caution':'Complete invalid output strict0, alignment unavailable; infrastructure/unrun null; no order or answer repair',
        'diagnostic':'Previous-record agreement descriptive only; position1 has no previous tag; retain multiset chance and repeated-label caveat'}


anchor.corr.fixed.make_request=make_request
anchor.corr.fixed.score_coordinate=score_coordinate
anchor.corr.fixed.leaf.score_labels=score_labels
anchor.corr.fixed.leaf.write_once=write_once
collect_calls=anchor.corr.fixed.collect_calls
