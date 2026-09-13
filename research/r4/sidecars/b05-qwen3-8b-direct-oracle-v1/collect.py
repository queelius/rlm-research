"""Only four direct and four exact-report oracle B05 calls."""
import concurrent.futures,importlib.util,sys
from pathlib import Path
import study
old=sys.modules.get('runner_study');sys.modules['runner_study']=study
try:
    source=study.load('b05_qwen8_collector_source',study.SOURCE/'runner_collect.py')
finally:
    if old is None:sys.modules.pop('runner_study',None)
    else:sys.modules['runner_study']=old

def execute(endpoint,output,deadline):
    c=source.Collector(endpoint,output,deadline);errors=[]
    def one(root):
        planned=[x for x in study.calls() if x['root_id']==root['root_id']]
        for call in planned:
            if call['kind']=='direct':prompt=root['direct_prompt'];reports=None
            else:reports=study.host_by_root()[root['root_id']]['exact_child_reports'];prompt=study.host_by_root()[root['root_id']]['oracle_synthesis_prompt']
            prompt=study.contract().clarify(call,prompt);c.call(call,prompt,root=root['safe_root'],reports=reports)
        study.write_x(output/'roots'/(root['root_id']+'.json'),{'root_id':root['root_id'],'planned_call_ids':[study.call_id(x) for x in planned],'all_2_accounted':len(planned)==2})
    with concurrent.futures.ThreadPoolExecutor(max_workers=study.CONCURRENCY) as pool:
        futures={pool.submit(one,r):r['root_id'] for r in study.roots()}
        for f in concurrent.futures.as_completed(futures):
            try:f.result()
            except Exception as e:errors.append({'root_id':futures[f],'type':type(e).__name__,'detail':str(e)})
    return {'physical_started':c.physical,'unique_provider_ids':len(c.provider_ids),'errors':errors}
