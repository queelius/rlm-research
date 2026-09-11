"""Pinned AG News first256; exact disjoint-prefix × tag × fixed-weight grid."""
import hashlib
import importlib.util
import itertools
import json
import unicodedata
from collections import Counter,defaultdict
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
PARENT=SIDE/'leaf-identity-factorial-v1'
CACHE=Path('/project/alex_phd/research-cache/datasets/fancyzhx--ag_news--eb185aade064a813bc0b7f42de02595523103ca4')
FEASIBILITY=SIDE.parent/'ideas/2026-09-09-agnews-identity-weight-feasibility.json'
DESIGN=SIDE.parent/'ideas/2026-09-09-agnews-identity-weight-screen.md'
DECISION=SIDE.parent/'operations/2026-09-09-continuous-allocation/AGNEWS_IMPLEMENTATION_DECISION.md'
PINS={PARENT/'study.py':'6294d813146cc75902cc5b61838046ed211ee8bc9002118a0bddd9dc9b06868e',
      PARENT/'SPEC.json':'150e2510a804042dc499fc1b9d8a195473d9f697c784a2bb929a803e96417792',
      FEASIBILITY:'9453b0f2a692e4a88513151ddda6bc595a04d90b1407ef333ede2d3af1750a84',
      DESIGN:'d42483488566928501f22d8a899165ecb902a41b9a05c08411ad1cfda5bca6c0',
      CACHE/'ACQUISITION.json':'bba780a2e3cdc34b6f7d9ee48a86cd613a8dda9a500b8fc623bea11f58622f54',
      CACHE/'test.parquet':'71de87ec66bc5737752a2502204dfa6d7fe9856ade3ea444dc6317789a4f13fb'}
for path,sha in PINS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest()!=sha: raise ValueError('pinned source changed: '+str(path))
loader=importlib.util.spec_from_file_location('agnews_private_factorial',PARENT/'study.py')
factorial=importlib.util.module_from_spec(loader);loader.loader.exec_module(factorial)
counter,padding,anchor=factorial.counter,factorial.padding,factorial.anchor
read,digest,file_hash,serialize,write_once=factorial.read,factorial.digest,factorial.file_hash,factorial.serialize,factorial.write_once
INPUT_MARKER=factorial.INPUT_MARKER
MASTER=981275401
SEEDS=[981275411,981275421]
ARMS=['meaningful_tag','ordinal_tag','constant_tag']
ALIASES={'original':'strict-rlm-qwen3-4b-role-original-v1','old_sft':'strict-rlm-qwen3-4b-role-sft-selected-v1'}
ALIAS=ALIASES['original']
LABELS=['World','Sports','Business','Sci/Tech']
DEFINITIONS=read(FEASIBILITY)['definitions']
expected_tags=factorial.expected_tags


def build_data():
    import pyarrow.parquet as pq
    if file_hash(CACHE/'test.parquet')!=PINS[CACHE/'test.parquet']: raise ValueError('dataset bytes changed')
    rows=pq.read_table(CACHE/'test.parquet').to_pylist()
    grouped=defaultdict(list)
    for index,row in enumerate(rows):
        normalized=' '.join(unicodedata.normalize('NFKC',row['text']).casefold().split())
        gid=hashlib.sha256(normalized.encode()).hexdigest()
        grouped[gid].append({'source_row_index':index,'question':row['text'],'source_label':row['label'],
            'group_id':gid,'gold_label':LABELS[row['label']]})
    conflicts={gid for gid,v in grouped.items() if len({x['source_label'] for x in v})>1}
    if conflicts or len(rows)!=7600 or len(grouped)!=7600:
        raise ValueError('pinned duplicate/conflict census changed; no reselection permitted')
    selected=sorted(grouped)[:256]
    if digest(selected)!='1b7b1c675bac3b7e8521ff2534a681f8e6dc3274234e978610c21ac2d4f4f88c':
        raise ValueError('approved first256 group list changed')
    eligible=[v for v in range(1000,10000) if not 1<=v%1000<=64]
    contexts=[]
    proof=read(FEASIBILITY)
    for index in range(4):
        cid=f'agnews-test-{index:02d}'
        records=[{**grouped[gid][0],'id':f'q{j+1:04d}','source_position':j+1,
            'source_row_indexes':[v['source_row_index'] for v in grouped[gid]]}
            for j,gid in enumerate(selected[index*64:(index+1)*64])]
        order=sorted(range(64),key=lambda j:digest([ROOT.name,MASTER,'display',cid,records[j]['group_id']]))
        values=sorted(eligible,key=lambda v:digest([ROOT.name,MASTER,'disjoint-value',cid,v]))[:64]
        if factorial.affine_sequence(values) or factorial.affine_sequence([values[j] for j in order]):
            raise ValueError('affine rank or display mapping; no automatic alternative')
        candidate=proof['contexts'][index]
        if ([records[j]['group_id'] for j in order]!=candidate['source_group_ids_in_display_order']
            or [values[j] for j in order]!=candidate['source_numbers_in_display_order']):
            raise ValueError('approved display/numeral assignment changed')
        contexts.append({'index':index,'source_context_id':cid,'dataset':'agnews','records':records,
            'presentations':[order],'disjoint_values_by_rank':values})
    return {'contexts':contexts,'master_seed':MASTER,'sampling_seeds':SEEDS,
        'selected_groups_sha256':digest(selected),'selection':'First256 lexical normalized hashes; full original text; no outcome/label/length filter',
        'source_provenance':read(CACHE/'ACQUISITION.json'),
        'dedup':{'rows':len(rows),'normalized_groups':len(grouped),'duplicate_groups':0,'conflicting_groups':0},
        'freshness':'New AG News task/test texts to this candidate study; pretraining/historical contamination unknown, not fresh SST'}


def build_design(data):
    prior=read(PARENT/'SPEC.json')['design']
    d={'contract':deepcopy(prior['contract']),'labels':LABELS,'definitions':DEFINITIONS,
       'task_labels':{'agnews':LABELS},'task_definitions':{'agnews':DEFINITIONS},
       'contexts':deepcopy(data['contexts']),'model_alias':ALIAS,'model_aliases':ALIASES,
       'max_tokens':3072,'max_concurrent_calls':4,'call_timeout_seconds':120,'wall_time_cap_seconds':900,
       'plan':[],'coordinates':[],'batches':[]}
    conditions=list(itertools.product(('q','p'),ARMS))
    for c in d['contexts']:
        index=c['index'];order=c['presentations'][0]
        for repeat,seed in enumerate(SEEDS):
            shift=(2*index+repeat)%6
            cycle=list(range(6));cycle=cycle[shift:]+cycle[:shift]
            if (index+repeat)%2: cycle.reverse()
            for position,j in enumerate(cycle):
                prefix,arm=conditions[j]
                weights=list(ALIASES) if (index+repeat+j)%2==0 else list(reversed(ALIASES))
                records=[{**deepcopy(c['records'][rank]),'input_position':i+1,'source_rank':rank+1,
                    'id':f"{prefix}{c['disjoint_values_by_rank'][rank]:04d}"} for i,rank in enumerate(order)]
                for weight_order,weight in enumerate(weights):
                    row={'dataset':'agnews','context_index':index,'source_context_id':c['source_context_id'],
                        'weight':weight,'source_prefix':prefix,'number_namespace':'disjoint','arm':arm,'grammar':'exact',
                        'seed':seed,'repeat':repeat,'size':64,'permutation':0,'start':0,'condition_index':j,
                        'cell_order':position,'weight_order':weight_order,'batch_id':len(d['batches']),'dispatch_order':len(d['plan'])}
                    row['id']=row['coordinate_id']=digest([ROOT.name,row])
                    d['plan'].append(row);d['coordinates'].append(deepcopy(row))
                    d['batches'].append({'questions':[r['question'] for r in records],
                        'gold':{'records':deepcopy(records),'order':list(range(64)),'arm':arm,
                            'source_prefix':prefix,'number_namespace':'disjoint','labels':LABELS}})
    return d


def make_request(design,row):
    body=factorial.make_request(design,row)
    before='Classify the overall sentiment of each movie-review sentence.\n'
    if not body['messages'][1]['content'].startswith(before): raise ValueError('inherited task-opening seam changed')
    body['messages'][1]['content']='Classify the main topic of each news text.\n'+body['messages'][1]['content'][len(before):]
    body['model']=ALIASES[row['weight']]
    return body


def score_labels(content,gold):
    tags=expected_tags(gold['records'],gold['arm'],gold['source_prefix'])
    adapted={**gold,'arm':'meaningful_tag','records':[{**r,'id':tag} for r,tag in zip(gold['records'],tags,strict=True)]}
    return padding.score_labels(content,adapted)


def score_coordinate(design,coordinate,records):
    value=counter.score_coordinate(design,coordinate,records)
    value['class_count_l1']=sum(abs(v) for v in value['class_count_errors'].values()) if value['class_count_errors'] is not None else None
    return value


def summarize(design,records):
    by_id=defaultdict(list)
    for row in records: by_id[row['coordinate']['id']].append(row)
    coordinates=[score_coordinate(design,c,by_id[c['id']]) for c in design['coordinates']]
    fields=['weight','source_prefix','arm'];cells=[]
    for key in sorted({tuple(c['coordinate'][f] for f in fields) for c in coordinates}):
        rows=[c for c in coordinates if tuple(c['coordinate'][f] for f in fields)==key]
        items=[i for c in rows for i in c['records'] if i['aligned']]
        l1=[c['class_count_l1'] for c in rows if c['class_count_l1'] is not None]
        cells.append({**dict(zip(fields,key)),'dataset':'agnews','planned_calls':len(rows),
            'recorded_calls':sum(c['complete'] for c in rows),'observable_calls':sum(c['strict_correct_assignments'] is not None for c in rows),
            'valid_calls':sum(c['fully_valid'] for c in rows),'infrastructure_errors':sum(c['infrastructure_errors'] for c in rows),
            'planned_assignments':64*len(rows),'aligned_assignments':len(items),'canonical_correct':sum(i['correct'] for i in items),
            'whole64_correct':sum(c['strict_full64_correct']==1 for c in rows),'per_call_class_count_l1':l1,
            'mean_per_call_class_count_l1':sum(l1)/len(l1) if l1 else None,
            'confusion':[{'gold':g,'prediction':p,'count':n} for (g,p),n in sorted(Counter((i['gold'],i['prediction']) for i in items).items())],
            'usage':{k:sum(c['usage'][k] for c in rows) for k in rows[0]['usage']},
            'missing_usage':{k:sum(c['missing_usage'][k] for c in rows) for k in rows[0]['missing_usage']},
            'length_stops':sum(c['length_stops'] for c in rows),'call_wall_seconds_sum':sum(c['call_wall_seconds_sum'] for c in rows)})
    groups=defaultdict(dict)
    for value in coordinates:
        c=value['coordinate'];groups[c['context_index'],c['repeat'],c['source_prefix'],c['weight']][c['arm']]=value
    pairs=[]
    for (context,repeat,prefix,weight),arms in groups.items():
        for left,right in [('ordinal_tag','meaningful_tag'),('constant_tag','meaningful_tag'),('constant_tag','ordinal_tag')]:
            a,b=arms[left],arms[right];observed=a['strict_correct_assignments'] is not None and b['strict_correct_assignments'] is not None
            valid=a['fully_valid'] and b['fully_valid']
            pairs.append({'context_index':context,'repeat':repeat,'source_prefix':prefix,'weight':weight,'contrast':right+'_minus_'+left,
                'both_observed':observed,'jointly_valid':valid,
                'strict_difference':b['strict_correct_assignments']-a['strict_correct_assignments'] if observed else None,
                'semantic_difference':b['semantic_correct_among_aligned']-a['semantic_correct_among_aligned'] if valid else None})
    contrasts=defaultdict(dict)
    for pair in pairs:
        if pair['contrast']=='meaningful_tag_minus_ordinal_tag': contrasts[pair['context_index'],pair['repeat'],pair['source_prefix']][pair['weight']]=pair
    interactions=[]
    for (context,repeat,prefix),weights in contrasts.items():
        a,b=weights['original']['strict_difference'],weights['old_sft']['strict_difference']
        interactions.append({'context_index':context,'repeat':repeat,'source_prefix':prefix,
            'old_minus_original_meaningful_minus_ordinal':b-a if a is not None and b is not None else None})
    return {'coordinates':coordinates,'cells':cells,'paired_context_effects':pairs,'weight_interactions':interactions,
        'inference_context_clusters':4,'primary':'Displayed-record meaningful-minus-ordinal, each weight/prefix; old-minus-original interaction',
        'failure_caution':'Invalid complete=zero strict/unavailable alignment; infrastructure/unrun=null; no numeric rescue.',
        'scope':'New task and output-instruction/grammar package; four contexts, not6144 independent labels; no whole-RLM effect.',
        'count_caution':'Class-count cancellation can hide correspondence errors; per-call vectors retained.'}


anchor.corr.fixed.make_request=make_request
anchor.corr.fixed.score_coordinate=score_coordinate
anchor.corr.fixed.leaf.score_labels=score_labels
anchor.corr.fixed.leaf.write_once=write_once
collect_calls=anchor.corr.fixed.collect_calls
