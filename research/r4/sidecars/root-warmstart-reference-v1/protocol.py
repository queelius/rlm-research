"""Fixed eight blocks and three source-authenticated policies; no outcome selection."""
from collections import Counter
import re
import study as s
MASTER=981456001
def amend_query(text):
    before='Among records belonging to all four users,'
    return 'Across all records, regardless of which of u0, u1, u2, or u3 owns the record,'+text[len(before):] if text.startswith(before) else text
def phase_order():return sorted(s.ROOTS,key=lambda arm:s.digest([MASTER,'phase',arm]))
def answer(records,labels,q):
    rows=[r for r in records if r['user'] in q['users'] and labels[r['id']]==q['target']]
    if q['operator']=='count':return len(rows)
    if q['operator']=='distinct':return len({r['user'] for r in rows})
    if q['operator']=='weight':return sum(r['weight'] for r in rows)
    raise ValueError('unknown operator')
def build():
    source=s.inputs();ids=[f'readout-{i:02d}' for i in range(4)];public=[next(c for c in source['PUBLIC.json'] if c['id']==cid) for cid in ids];queries={};blocks=[];plan=[]
    for ci,c in enumerate(public):
        for family in ('count-union','distinct-all' if ci%2==0 else 'weight-single'):
            name=c['id']+':'+family;old=next(r for r in source['PLANS.json']['readout'] if r['task_name']==name);q=source['QUERIES.json'][name];text=source['TASKS.json'][name]['question'];index=len(blocks)
            queries[name]=dict(question=amend_query(text),original_question=text,query=q)
            if answer(c['records'],source['HOST_GOLD.json'][c['id']]['labels'],q)!=source['HOST_GOLD.json'][c['id']]['answers'][family]:raise ValueError('original gold differs from independent scalar reduction')
            block={**old,'seed':981456101+index,'repeat':0,'block':index,'block_id':s.digest([MASTER,'block',name]),'namespace':s.NAMESPACE,'arm':'typed'};block.pop('id');blocks.append(block)
    blocks=sorted(blocks,key=lambda b:s.digest([MASTER,'block-order',b['block_id']]))
    for root in phase_order():
        for position,block in enumerate(blocks):
            row={**block,'root':root,'position':position};row['id']=s.digest(row);plan.append(row)
    groups=[g for g in source['GROUPS.json'] if g['id'] in ids];gids=[g for row in groups for g in row['group_ids']]
    if len(gids)!=64 or len(set(gids))!=64 or set(gids)&set(source['PROVENANCE.json']['excluded_group_ids']):raise ValueError('source exposure boundary changed')
    answers=[source['HOST_GOLD.json'][b['context_id']]['answers'][b['family']] for b in blocks];hist=Counter(answers);best=max(hist.values())
    return {'PUBLIC.json':public,'HOST_GOLD.json':{c['id']:source['HOST_GOLD.json'][c['id']] for c in public},'QUERIES.json':queries,'PLAN.json':plan,'BLOCKS.json':blocks,'PHASES.json':phase_order(),'BINDINGS.json':{arm:s.binding(arm) for arm in phase_order()},'BASELINE_DISTRIBUTION.json':dict(unique_blocks=8,histogram=dict(hist),zero_correct=hist[0],best_constant_correct=best,best_constants=sorted(k for k,v in hist.items() if v==best),each_policy_same_blocks=True,selection_resampling=False),
        'PROVENANCE.json':dict(source_sha256={str(s.QSR/'inputs'/k):v for k,v in s.INPUT_PINS.items()},groups=groups,novelty='Already QSR readout/research-exposed;64 pinned prior-root-excluded groups, all c32-training-exposed; not new confirmation',common_all_scope_clarification=True,role='unchanged native coding',root_tools_optional_typed_children_unchanged=True,master=MASTER,seed_namespace=s.NAMESPACE,phase_order_confounded=True)}
def score(reply,gold,available):
    m=re.fullmatch(r'Answer: ([0-9]+)',reply.strip()) if available and isinstance(reply,str) else None
    return dict(available=available,format_valid=bool(m) if available else None,parsed=int(m[1]) if m else None,reward=int(bool(m and int(m[1])==gold)) if available else None,operational_success=int(bool(available and m and int(m[1])==gold)))
def null(row,cause):return dict(coordinate=row,available=False,format_valid=None,reward=None,operational_success=0,cause=cause)
