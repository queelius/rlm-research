"""Qualified semantic native task plus one optional source-only module."""
import hashlib
import json
import cl_study as s
import cl_protocol as p

old=s.load('cl_qualified_sm_native',s.SM/'sm_native.py','0e7e46a8b17c0752b72b635e4c2178ab0bd2b0571863c18907886f7a56690f4b',{'sm_study':s,'sm_protocol':p})
expected,environment_config,interface,make_context,installed=old.expected,old.environment_config,old.interface,old.make_context,old.installed

def task(context,query,row,map_raw):
    if row['representation'] not in ('FILE','LOADER'):raise ValueError('native source-access arm')
    result=old.task(context,query,row,map_raw);original_type=type(result)
    module=p.module_source(json.dumps(context['records'],ensure_ascii=False),map_raw)
    class LoaderTask(original_type):
        async def setup(self,trace,runtime):
            await super().setup(trace,runtime)
            receipt=trace.info['semantic_map_setup']
            module_hash=None
            if row['representation']=='LOADER':
                await runtime.write('source_state.py',module.encode())
                actual=await runtime.read('source_state.py',max_bytes=2*1024*1024)
                if actual!=module.encode():raise ValueError('canonical module bytes differ')
                module_hash=hashlib.sha256(actual).hexdigest()
            trace.info['canonical_loader_setup']={**receipt,'loader_available':row['representation']=='LOADER',
                'module_sha256':module_hash,'return_shape':{'records':'list[dict]','predictions':'dict[str,str]'},
                'no_automatic_restore':True,'canonical_module_contains_query_or_gold':False}
    result.__class__=LoaderTask
    result.data=result.data.model_copy(update={'source_split':'QSR-research-operator-SFT-child-training-exposed'})
    return result
