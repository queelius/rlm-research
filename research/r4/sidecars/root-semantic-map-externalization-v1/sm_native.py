"""Common raw records/query/map files; only new user-message map visibility differs."""
import hashlib
import json
import sm_study as s
import sm_protocol as p
old=s.load('sm_qualified_native_capture',s.CE/'native.py','35ec43e9a41cfc87450371900e7205989fc592e0d28e4f6918e22c76316b295d',{'study':s,'protocol':p})
expected,environment_config,interface,make_context,installed=old.expected,old.environment_config,old.interface,old.make_context,old.installed

def task(context,query,row,map_raw):
    if row['role']!='native':raise ValueError('current native role only')
    p.map_state(map_raw,[r['id'] for r in context['records']])
    result=s.qnative().make_task(context,query,0,row['id']);original_type=type(result)
    class MapTask(original_type):
        async def setup(self,trace,runtime):
            await super().setup(trace,runtime)
            await runtime.write('labels.json',map_raw.encode())
            expected_files={'records.json':json.dumps(context['records'],ensure_ascii=False),'context.txt':context['text'],'query.txt':query,'labels.json':map_raw}
            actual={}
            for name,value in expected_files.items():
                raw=await runtime.read(name,max_bytes=2*1024*1024)
                if raw!=value.encode():raise ValueError('common public/map bytes differ: '+name)
                actual[name]=hashlib.sha256(raw).hexdigest()
            trace.info['semantic_map_setup']=dict(file_sha256=actual,role='native',representation=row['representation'],no_gold=True,plain_query=query)
    result.__class__=MapTask
    result.plain_query=query
    result.data=result.data.model_copy(update={'prompt':p.prompt(context,query,map_raw,row['representation'])})
    return result
