"""Original public records and semantic gold; amended common scope, fresh paired seeds."""
import re
import study as s
ARMS=(('native','raw'),('native','map'),('compact','raw'),('compact','map'))
COMPACT="Solve the user's task. Tools are optional. When finished, return only Answer: N with a nonnegative integer."
def amend_query(text):
    before='Among records belonging to all four users,'
    if text.startswith(before):return 'Across all records, regardless of which of u0, u1, u2, or u3 owns the record,'+text[len(before):]
    return text
def build():
    source=s.inputs();public=source['PUBLIC.json'][:2]
    if [c['id'] for c in public]!=['training-00','training-01']:raise ValueError('first contexts differ')
    queries={};plan=[];block=0
    for c in public:
        candidates={r['task_name']:r for rows in source['PLANS.json']['training'].values() for r in rows if r['context_id']==c['id']}
        for name in sorted(candidates):
            original=source['TASKS.json'][name]['question'];query=source['QUERIES.json'][name]
            queries[name]=dict(original=original,question=amend_query(original),query=query)
            seed=981421101+block
            for position,(role,evidence) in enumerate(ARMS[block%4:]+ARMS[:block%4]):
                row={**candidates[name],'role':role,'evidence':evidence,'seed':seed,'repeat':0,'arm':'typed','block':block,'position':position,'namespace':s.NAMESPACE}
                row.pop('id');row.pop('candidate_window',None);row['id']=s.digest(row);plan.append(row)
            block+=1
    return {'PUBLIC.json':public,'HOST_GOLD.json':{c['id']:source['HOST_GOLD.json'][c['id']] for c in public},'QUERIES.json':queries,'PLAN.json':plan,
        'ACQUISITION_PLAN.json':[dict(id=s.digest([s.NAMESPACE,'source',c['id']]),context_id=c['id'],seed=981421201+i) for i,c in enumerate(public)],
        'PROVENANCE.json':dict(source_sha256={str(s.QSR/'inputs'/k):v for k,v in s.INPUT_PINS.items()},groups=[g for g in source['GROUPS.json'] if g['id'] in {c['id'] for c in public}],source_novelty='QSR exposed training contexts; no fresh-data claim',common_scope_clarification=True,paired_seed_namespace=s.NAMESPACE)}
def map_state(raw,ids):
    try:return dict(available=True,labels=s.contract().strict_map(raw,ids),raw=raw,error=None)
    except Exception as error:return dict(available=False,labels=None,raw=raw,error=dict(type=type(error).__name__,message=str(error)))
def answer(records,labels,q):
    rows=[r for r in records if r['user'] in q['users'] and labels[r['id']]==q['target']]
    if q['operator']=='count':return len(rows)
    if q['operator']=='distinct':return len({r['user'] for r in rows})
    if q['operator']=='weight':return sum(r['weight'] for r in rows)
    raise ValueError('operator')
def score(reply,gold,available):
    m=re.fullmatch(r'Answer: ([0-9]+)',reply.strip()) if available and isinstance(reply,str) else None
    return dict(available=available,format_valid=bool(m) if available else None,parsed=int(m[1]) if m else None,reward=int(bool(m and int(m[1])==gold)) if available else None,operational_success=int(bool(available and m and int(m[1])==gold)))
def prompt(c,q,map_raw=None):
    text=s.qnative().prompt(c,q)
    if map_raw is not None:text+='\n\nThe following complete ID-to-category map consists of actual child predictions, not dataset truth. It is additional evidence; tools remain optional.\n'+map_raw
    return text
def null(row,cause):return dict(coordinate=row,available=False,format_valid=None,reward=None,operational_success=0,cause=cause)
