"""Qualified source/native collector with bounded counted study-specific adaptations."""
import asyncio
import functools
import sys
import types
import sm_study as s
import sm_protocol as p
import sm_native as n
EDIT_COUNTS={}

@functools.lru_cache(maxsize=1)
def implementation():
    path=s.CE/'collect.py';s.check(path,'38f4b840b3e8d1fec681ead071d5d83c50d6a6ae199930ec52f6cb1a03ac8487');source=path.read_text()
    edits={
        'imports':('import native as n\nimport protocol as p\nimport study as s','import sm_native as n\nimport sm_protocol as p\nimport sm_study as s'),
        'owner_path':("s.ROOT/'owner.py'","s.ROOT/'sm_owner.py'"),
        'planned_count':('planned=24','planned=48'),
        'sources_count':('source_acquisitions=2','source_acquisitions=8'),
        'closure_reserve':('deadline=args.deadline-15','deadline=args.deadline-120'),
        'stage_caps':('await dispatch(sources,acquire,min(deadline,time.time()+150))',"source_deadline=min(deadline-1500,time.time()+300)\n        await dispatch(sources,acquire,source_deadline)\n        deadline=min(deadline,time.time()+1500)\n        s.write(args.output/'STAGE_DEADLINES.json',dict(source_deadline_epoch=source_deadline,root_deadline_epoch=deadline,root_reserved_seconds=1500,source_cap_seconds=300))"),
        'setup_receipt':("get('contract_evidence_setup')","get('semantic_map_setup')"),
        'mechanism_metric':("result['actual_scoped_reduction']=None;", "result['actual_scoped_reduction']=None;result['co_primary_executed_map_reduction_requires_audit']=True;"),
    }
    for name,(before,after) in edits.items():
        expected=2 if name in ('owner_path','planned_count') else 1
        if source.count(before)!=expected:raise ValueError('counted source edit: '+name)
        source=source.replace(before,after);EDIT_COUNTS[name]=expected
    module=types.ModuleType('sm_qualified_collector_composition');module.__file__=str(path);sys.modules[module.__name__]=module
    with s.aliases({'sm_study':s,'sm_protocol':p,'sm_native':n}):exec(compile(source,str(path)+'::semantic-map48','exec'),module.__dict__)
    original=module.extraction_request
    def typed_request(context,row,binding):
        body=original(context,row,binding);st=s.qnative().stack();catalog=st.interface.catalogs({context['id']:context})[str(context['native_context_id'])]
        matched=st.interface.hooks.contract.match_request(body['messages'][1]['content'],catalog)
        if not matched['matched']:raise ValueError('exact typed source catalog match')
        body['structured_outputs']={'json':matched['schema']};return body
    module.extraction_request=typed_request
    return module

def extraction_request(*args):return implementation().extraction_request(*args)
def __getattr__(name):return getattr(implementation(),name)
if __name__=='__main__':
    module=implementation();raise SystemExit(asyncio.run(module.run(module.parse_args())))
