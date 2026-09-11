"""Canonical source access only; no task-dependent code in the optional module."""
import json
import cl_study as s

old=s.load('cl_qualified_sm_protocol',s.SM/'sm_protocol.py','4227814dbd4613fc67ac1cf3f3c34fd15e6ad5fb112582ae5b56579689d31efa',{'sm_study':s})
map_state,answer,score,null=old.map_state,old.answer,old.score,old.null
COMPACT=old.COMPACT
SOURCE_MANIFEST=s.SIDE.parent/'analyses/root-semantic-map-externalization-live-2026-09-10/OUTCOME_PINS_V2.json'
SOURCE_MANIFEST_SHA='6be63af9e2f2af6927e9e86d1767d6200093f05e3fa88b9e857827e879505e2b'
API_DESCRIPTION=("Optional Python source access: source_state.py provides source_state.load(). It returns a fresh ordinary dict with exactly 'records' (the original list of id/user/text/weight record dicts) and 'predictions' (the original record-ID-to-predicted-category dict). Each call decodes the same canonical source snapshots; editing returned objects does not change later loads. It does not interpret query.txt, classify, select, aggregate or answer. Importing or calling it is optional.")

def module_source(records_json,map_raw):
    if not isinstance(records_json,str) or not isinstance(map_raw,str):raise TypeError('canonical source text')
    return ('"""Optional canonical source copies; no task logic or automatic calls."""\n'
        'import json as _json\n'
        'def _make_loader(records_raw, predictions_raw):\n'
        '    def load():\n'
        '        return {"records": _json.loads(records_raw), "predictions": _json.loads(predictions_raw)}\n'
        '    return load\n'
        f'load = _make_loader({records_json!r}, {map_raw!r})\n'
        'del _make_loader\n')

def build():
    s.check(s.SM/'READY.json','953eaf07242127050415bc922c3b08b9a4fa94f03f5f124ea08f9ff3ec73c7c5')
    ready=s.read(s.SM/'READY.json');values={}
    for name in ('PUBLIC.json','HOST_GOLD.json','QUERIES.json','PLAN.json','ACQUISITION_PLAN.json','PROVENANCE.json'):
        path=s.SM/'inputs'/name;s.check(path,ready['input_sha256'][str(path)]);values[name]=s.read(path)
    s.check(SOURCE_MANIFEST,SOURCE_MANIFEST_SHA);pins=s.read(SOURCE_MANIFEST)['sha256'];reused=[]
    for source in values['ACQUISITION_PLAN.json']:
        path=s.SM/'outputs/attempt-001/rollout/acquisitions'/(source['id']+'.json');s.check(path,pins[str(path)]);record=s.read(path)
        if record['coordinate']!=source:raise ValueError('historical acquisition coordinate')
        reused.append(dict(coordinate=source,path=str(path),sha256=pins[str(path)],record=record,
            reuse_only=True,new_physical_request=False))
    plan=[]
    for block in range(24):
        original=next(r for r in values['PLAN.json'] if r['block']==block)
        order=('FILE','LOADER') if block%2==0 else ('LOADER','FILE')
        for position,representation in enumerate(order):
            row={**original,'namespace':s.NAMESPACE,'seed':981631101+block,'position':position,'representation':representation}
            row.pop('id');row['id']=s.digest(row);plan.append(row)
    values['PLAN.json']=plan;values['REUSED_SOURCES.json']=reused
    values['PROVENANCE.json']={**values['PROVENANCE.json'],'parent_study':str(s.SM),
        'new_source_acquisitions':0,'reused_completed_acquisitions':8,'paired_seed_namespace':s.NAMESPACE,
        'canonical_module_query_independent':True,'source_manifest':str(SOURCE_MANIFEST),'source_manifest_sha256':SOURCE_MANIFEST_SHA,
        'prior_outcome_motivation_exposed':True,'source_split_metadata_corrected_common_both_arms':True}
    return values

def reused_source(row):
    entries=s.read(s.ROOT/'inputs/REUSED_SOURCES.json')
    entry=next(e for e in entries if e['coordinate']==row)
    s.check(entry['path'],entry['sha256'])
    return entry['record']

def prompt(context,query,map_raw,representation):
    if representation not in ('FILE','LOADER'):raise ValueError('loader arm')
    base=old.prompt(context,query,map_raw,'FILE')
    return base if representation=='FILE' else base+'\n\n'+API_DESCRIPTION
