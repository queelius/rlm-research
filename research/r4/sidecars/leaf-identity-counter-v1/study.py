"""Identity versus ordinal96: label-independent assignment and private frozen helpers."""
import hashlib
import importlib.util
import itertools
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PARENT = SIDE / 'leaf-anchor-padding-control-v1'
PINS = {PARENT/'study.py':'d8cc897b670929acc3b19c75ff9b01ee963afecf13935d92a426f88b14060a9b',
        PARENT/'driver.py':'045355caa4955addd1936cfb756b0ff35f8578492045cc41644c03ccc2cdbe83',
        PARENT/'owned.py':'206e50a913727e0f66b6bb26002ff07ec75d7c763a4a23715f6e56c4cff65f53',
        PARENT/'SPEC.json':'90d3ed6ca7acfee9f5e5c3f3dae4000ac6fc1e0f2dacceeba5fd500d69cf1f94'}
for path, expected in PINS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('frozen padding changed')
loader=importlib.util.spec_from_file_location('counter_private_padding',PARENT/'study.py')
padding=importlib.util.module_from_spec(loader)
loader.loader.exec_module(padding)
anchor=padding.anchor
read,digest,file_hash,serialize,write_once=padding.read,padding.digest,padding.file_hash,padding.serialize,padding.write_once
INPUT_MARKER=padding.INPUT_MARKER
ALIAS=padding.ALIAS
MASTER=981266001
ARMS=['meaningful_tag','ordinal_tag','constant_tag']
SEEDS=[int(digest([ROOT.name,MASTER,'sampling',i])[:8],16)%2147483647 for i in range(2)]


def build_data(source):
    data=deepcopy(source)
    for c in data['contexts']:
        records=c['records']
        ranked=sorted(range(64),key=lambda j:digest([ROOT.name,MASTER,'source-id',c['source_context_id'],records[j]['group_id']]))
        ranks={j:i+1 for i,j in enumerate(ranked)}
        c['records']=[{**r,'parent_id':r['id'],'id':f'q{ranks[j]:04d}'} for j,r in enumerate(records)]
        c['presentations']=[sorted(range(64),key=lambda j:digest([ROOT.name,MASTER,'presentation',c['source_context_id'],p,records[j]['group_id']])) for p in range(2)]
    data.update(master_seed=MASTER,sampling_seeds=SEEDS,
        source_path=str(PARENT/'DATA.json'),source_sha256=file_hash(PARENT/'DATA.json'),
        assignment_rule='Ascending SHA256(namespace,master,source-id,source_context_id,group_id); rank gives q0001..q0064',
        presentation_rule='Independent ascending SHA256(namespace,master,presentation,source_context_id,permutation,group_id)',
        freshness='Exact exposed developmental eight contexts; no new unseen-data claim')
    return data


def expected_tags(records,arm):
    if arm=='meaningful_tag':return [r['id'] for r in records]
    if arm=='ordinal_tag':return [f'p{i:04d}' for i in range(1,len(records)+1)]
    if arm=='constant_tag':return ['p0000']*len(records)
    raise ValueError('unknown arm')


def build_design(data):
    previous=read(PARENT/'SPEC.json')['design']
    d={k:deepcopy(previous[k]) for k in ['contract','labels','definitions','task_labels','task_definitions']}
    d.update(contexts=deepcopy(data['contexts']),model_alias=ALIAS,model_aliases={'old_sft':ALIAS},
        max_tokens=3072,max_concurrent_calls=4,call_timeout_seconds=120,wall_time_cap_seconds=600,
        plan=[],coordinates=[],batches=[])
    orders=list(itertools.permutations(ARMS))
    for c in d['contexts']:
        for permutation,order in enumerate(c['presentations']):
            records=[{**deepcopy(c['records'][j]),'input_position':i+1} for i,j in enumerate(order)]
            for repeat,seed in enumerate(SEEDS):
                group_index=c['index']*4+permutation*2+repeat
                for position,arm in enumerate(orders[group_index%6]):
                    row={'dataset':c['dataset'],'context_index':c['index'],'source_context_id':c['source_context_id'],
                        'weight':'old_sft','arm':arm,'grammar':'exact','seed':seed,'repeat':repeat,'size':64,
                        'permutation':permutation,'start':0,'cell_order':position,'batch_id':len(d['batches']),
                        'dispatch_order':len(d['plan'])}
                    row['id']=row['coordinate_id']=digest([ROOT.name,row])
                    d['plan'].append(row)
                    d['coordinates'].append(deepcopy(row))
                    d['batches'].append({'questions':[r['question'] for r in records],
                        'gold':{'records':deepcopy(records),'order':list(range(64)),'arm':arm,'labels':d['task_labels'][c['dataset']]}})
    return d


def make_request(design,row):
    body=anchor.make_request(design,{**row,'arm':'anonymous'})
    records=design['batches'][row['batch_id']]['gold']['records']
    prefix,rest=body['messages'][1]['content'].split('Return only',1)
    rest=rest.split('\nAllowed labels:',1)[1]
    instruction='Return only a JSON array of objects in displayed input order, exactly one object per input record. Each object has exactly the keys tag then label. '
    instruction+={'meaningful_tag':'Set tag to the corresponding randomized source ID shown in the input and label to that record\'s label.',
        'ordinal_tag':'Set tag to the displayed position counter p0001, p0002, through p0064, and label to the corresponding displayed record\'s label. These position tags are not source IDs.',
        'constant_tag':'Set tag to the literal "p0000" in every object and label to the corresponding displayed record\'s label. This constant tag is not a source ID.'}[row['arm']]
    body['messages'][1]['content']=prefix+instruction+'\nAllowed labels:'+rest
    items=[{'type':'object','properties':{'tag':{'type':'string','const':tag},
        'label':{'type':'string','enum':design['task_labels'][row['dataset']]}},
        'required':['tag','label'],'additionalProperties':False} for tag in expected_tags(records,row['arm'])]
    body['structured_outputs']={'json':{'type':'array','prefixItems':items,'items':False,'minItems':64,'maxItems':64}}
    return body


def score_labels(content,gold):
    # Reuse exact frozen ordered-tag scorer; expected tags never change semantic label alignment.
    adapted={**gold,'arm':'meaningful_tag','records':[
        {**record,'id':tag} for record,tag in zip(gold['records'],expected_tags(gold['records'],gold['arm']))]}
    return padding.score_labels(content,adapted)


def score_coordinate(design,coordinate,records):
    value=padding.score_coordinate(design,coordinate,records)
    aligned=value['aligned_records']==64 and value['complete'] and not value['infrastructure_errors']
    value['class_count_vector_exact']=None
    value['class_count_errors']=None
    value['object_key_orders']=None
    if aligned:
        gold=Counter(r['gold'] for r in value['records'])
        predicted=Counter(r['prediction'] for r in value['records'])
        value['class_count_errors']={label:predicted[label]-gold[label] for label in design['task_labels'][coordinate['dataset']]}
        value['class_count_vector_exact']=all(v==0 for v in value['class_count_errors'].values())
        content=records[0]['raw_response']['choices'][0]['message']['content']
        parsed=json.loads(content,object_pairs_hook=anchor.corr.strict_object)
        value['object_key_orders']=dict(Counter(','.join(item) for item in parsed))
    return value


def summarize(design,records):
    # Frozen cell summaries are valid for arbitrary ARMS; replace only the pair grouping
    # because this study adds presentation permutations and two new arm contrasts.
    padding.ARMS=ARMS
    out=padding.summarize(design,records)
    out['coordinates']=[score_coordinate(design,c,[r for r in records if r['coordinate']['id']==c['id']]) for c in design['coordinates']]
    out['cells']=[cell for cell in out['cells'] if cell['planned_calls']]
    grouped=defaultdict(dict)
    for value in out['coordinates']:
        c=value['coordinate']
        grouped[c['dataset'],c['context_index'],c['permutation'],c['repeat']][c['arm']]=value
    pairs=[]
    for key,arms in grouped.items():
        for left,right in [('ordinal_tag','meaningful_tag'),('constant_tag','ordinal_tag'),('constant_tag','meaningful_tag')]:
            a,b=arms[left],arms[right]
            observed=a['strict_correct_assignments'] is not None and b['strict_correct_assignments'] is not None
            valid=a['fully_valid'] and b['fully_valid']
            pairs.append({'dataset':key[0],'context_index':key[1],'permutation':key[2],'repeat':key[3],
                'contrast':right+'_minus_'+left,'both_observed':observed,'jointly_valid':valid,
                'strict_difference':b['strict_correct_assignments']-a['strict_correct_assignments'] if observed else None,
                'semantic_difference':b['semantic_correct_among_aligned']-a['semantic_correct_among_aligned'] if valid else None})
    out['paired_context_effects']=pairs
    out['inference_unit']='Four exposed context groups per task; permutations/seeds nested. Identity versus ordinal, not an attention-mechanism proof.'
    return out


anchor.corr.fixed.make_request=make_request
anchor.corr.fixed.score_coordinate=score_coordinate
anchor.corr.fixed.leaf.score_labels=score_labels
anchor.corr.fixed.leaf.write_once=write_once
collect_calls=anchor.corr.fixed.collect_calls
