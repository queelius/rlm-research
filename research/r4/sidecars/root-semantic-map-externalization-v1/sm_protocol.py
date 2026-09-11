"""Fixed paired representation only; no authored algorithm or semantic source selection."""
import sm_study as s
old=s.load('sm_qualified_ce_protocol',s.CE/'protocol.py','b4caa1edb0bb8fab8d4959276772e543d25d530c7ddb1c7b7e43232ff0a78480',{'study':s})
map_state,answer,score,null=old.map_state,old.answer,old.score,old.null
COMPACT=old.COMPACT # unused; qualified native module export compatibility, never selected.
def build(source=None):
    source=source or s.inputs();public=source['PUBLIC.json'][:8]
    if [c['id'] for c in public]!=[f'training-{i:02}' for i in range(8)]:raise ValueError('fixed exposed contexts')
    queries={};plan=[];block=0
    for context in public:
        candidates={r['task_name']:r for rows in source['PLANS.json']['training'].values() for r in rows if r['context_id']==context['id']}
        if len(candidates)!=3:raise ValueError('three supported queries')
        for name in sorted(candidates):
            original=source['TASKS.json'][name]['question'];queries[name]=dict(original=original,question=old.amend_query(original),query=source['QUERIES.json'][name])
            order=('INLINE','FILE') if block%2==0 else ('FILE','INLINE')
            for position,representation in enumerate(order):
                row={**candidates[name], 'role':'native','evidence':'map','representation':representation,'seed':981512101+block,'repeat':0,'arm':'typed','block':block,'position':position,'namespace':s.NAMESPACE}
                row.pop('id');row.pop('candidate_window',None);row['id']=s.digest(row);plan.append(row)
            block+=1
    return {'PUBLIC.json':public,'HOST_GOLD.json':{c['id']:source['HOST_GOLD.json'][c['id']] for c in public},'QUERIES.json':queries,'PLAN.json':plan,
        'ACQUISITION_PLAN.json':[dict(id=s.digest([s.NAMESPACE,'source',c['id']]),context_id=c['id'],seed=981512201+i) for i,c in enumerate(public)],
        'PROVENANCE.json':dict(source_sha256={str(s.QSR/'inputs'/k):v for k,v in s.INPUT_PINS.items()},groups=[g for g in source['GROUPS.json'] if g['id'] in {c['id'] for c in public}],source_novelty='QSR research/child/SFT exposed training00-07, not fresh',common_scope_clarification=True,paired_seed_namespace=s.NAMESPACE,typed_sources_differ_from_historical_ce_free_json=True)}
def prompt(context,query,map_raw,representation):
    if representation not in ('INLINE','FILE') or not isinstance(map_raw,str):raise ValueError('eligible actual map and arm')
    text=s.qnative().prompt(context,query)+'\n\nlabels.json contains a complete JSON object mapping record IDs to canonical question categories. These are actual child predictions, not dataset truth. This is additional evidence; tools and further child calls remain optional. The same map may also be displayed below.'
    return text+'\n\n'+map_raw if representation=='INLINE' else text
