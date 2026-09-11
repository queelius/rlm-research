"""Qualified native collector; old sources reused without any acquisition POST."""
import asyncio
import functools
import sys
import types
import cl_study as s
import cl_protocol as p
import cl_native as n
EDIT_COUNTS={}

@functools.lru_cache(maxsize=1)
def implementation():
    path=s.CE/'collect.py';s.check(path,'38f4b840b3e8d1fec681ead071d5d83c50d6a6ae199930ec52f6cb1a03ac8487');source=path.read_text()
    edits={
        'imports':('import native as n\nimport protocol as p\nimport study as s','import cl_native as n\nimport cl_protocol as p\nimport cl_study as s'),
        'owner_path':("s.ROOT/'owner.py'","s.ROOT/'cl_owner.py'"),
        'planned_count':('planned=24','planned=48'),
        'source_count':('source_acquisitions=2','source_acquisitions=0,reused_source_acquisitions=8'),
        'root_deadline':('deadline=args.deadline-15','deadline=min(args.deadline-30,time.time()+1440)'),
        'setup_receipt':("get('contract_evidence_setup')","get('canonical_loader_setup')"),
        'mechanism_metric':("result['actual_scoped_reduction']=None;", "result['actual_scoped_reduction']=None;result['actual_loader_use']=None;result['actual_source_abandonment']=None;"),
        'source_reuse_label':("result['source_acquisition_id']=source['coordinate']['id'] if row['evidence']=='map' else None", "result['source_acquisition_id']=source['coordinate']['id'] if row['evidence']=='map' else None\n        result['source_acquisition_is_historical_reuse']=True"),
    }
    for name,(before,after) in edits.items():
        expected=2 if name in ('owner_path','planned_count') else 1
        if source.count(before)!=expected:raise ValueError('counted source edit: '+name)
        source=source.replace(before,after);EDIT_COUNTS[name]=expected
    before='        async def acquire(row):';after="    out=args.output/'native';out.mkdir()"
    if source.count(before)!=1 or source.count(after)!=1:raise ValueError('bounded acquisition-region seam')
    start=source.index(before);end=source.index(after,start)
    source=source[:start]+'''        for row in sources:
            record=p.reused_source(row)
            context=contexts[row['context_id']]
            checked=verify_source(record['raw_response'],record['request'],tokenizer)
            parsed=p.map_state(checked['content'],[r['id'] for r in context['records']])
            if not checked['native_verified'] or not parsed['available'] or parsed!=record['map']:
                raise ValueError('frozen source structural/native gate changed')
            if record['request']['model']!=binding['fixed_child']:
                raise ValueError('reused source child differs')
            s.write(args.output/'reused-acquisitions'/(row['id']+'.json'),record)
            acquired[row['context_id']]=record
    s.write(args.output/'REUSED_SOURCE_SEAL.json',dict(new_source_physical_attempts=0,
        historical_sources={r['id']:s.sha(args.output/'reused-acquisitions'/(r['id']+'.json')) for r in sources}))
'''+source[end:]
    EDIT_COUNTS['replace_entire_source_dispatch_with_authenticated_reuse']=1
    module=types.ModuleType('cl_qualified_collector_composition');module.__file__=str(path);sys.modules[module.__name__]=module
    with s.aliases({'cl_study':s,'cl_protocol':p,'cl_native':n}):exec(compile(source,str(path)+'::canonical-loader48','exec'),module.__dict__)
    module.ledger=ledger
    return module

def ledger(output):
    module=implementation();rows=list(module.audits(output/'rollout/native').values())
    historical=[p.reused_source(row) for row in s.read(s.ROOT/'inputs/ACQUISITION_PLAN.json')]
    return dict(total=module.cost(rows),native=module.cost(rows),sources=module.cost([]),
        historical_source_once=module.cost(historical),full_context_pipeline_with_historical_once=module.cost(rows+historical),
        accounting='total is new native attempts/returned completions only; historical8 sources retained separately, reused six times each; per-endpoint hypothetical totals charge their original one source without claiming new acquisition',provider_billing=None)

def __getattr__(name):return getattr(implementation(),name)
if __name__=='__main__':
    module=implementation();raise SystemExit(asyncio.run(module.run(module.parse_args())))
