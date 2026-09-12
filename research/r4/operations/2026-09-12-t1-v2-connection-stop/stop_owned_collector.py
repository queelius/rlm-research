"""Stop authenticated T1 V2 after identifying the hardcoded T0.5 wire guard."""
import json
import os
from pathlib import Path
import signal
import time

ROOT=Path(__file__).resolve().parent
SIDE=Path('/project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-procedural-sft32-onpolicy-t1-v1')
NATIVE='/project/alex_phd/envs/prime-rl-5990b1b/bin/python'
def observe(pid):
    p=Path('/proc')/str(pid);s=p.joinpath('stat').read_text().rsplit(') ',1)[1].split()
    return {'pid':pid,'uid':p.stat().st_uid,'ppid':int(s[1]),'pgid':int(s[2]),'start_ticks':int(s[19]),
            'argv':[x.decode() for x in p.joinpath('cmdline').read_bytes().split(b'\0')[:-1]]}

parent=observe(818722);child=observe(819381)
assert parent['uid']==child['uid']==os.getuid()==1523821556
assert child['ppid']==parent['pid'] and child['pgid']==child['pid']
assert child['start_ticks']==1105043779
assert parent['argv']==[NATIVE,str(SIDE/'owner_v2.py'),'run','--output',str(SIDE/'outputs/attempt-002'),'--outer-seconds','1100']
assert child['argv']==[NATIVE,str(SIDE/'collect_v2.py'),'--phase','train','--arm','checkpoint32','--endpoint',str(SIDE/'outputs/attempt-002/owned-service/service/endpoint-original.json'),'--output',str(SIDE/'outputs/attempt-002/science'),'--deadline','1789247427.1232715']
calls=[json.loads(p.read_text()) for p in (SIDE/'outputs/attempt-002/science/native-calls').glob('*-result.json')]
assert len(calls)>=24 and all(c['status']=='error' and c['error']['type']=='ProviderError' and c['error']['message']=='Connection error.' for c in calls)
receipt={'epoch':time.time(),'authority':'MAIN','signal':'SIGTERM','target':child,'authenticated_owner':parent,
         'owner_retained_for_release':True,'observed_calls':len(calls),'returned_calls':0,
         'reason':'Actual role-audit wire_request rejects temperature1.0 because inherited native_routing guard hardcodes0.5. CPU fixture omitted this installed role hook; no scientific model returns. Preserve attempts and fix exact bound guard.',
         'cause_source':'sidecars/root-only-credit-v1/native_routing.py:wire_request',
         'no_files_deleted':True,'original_outcomes_unchanged':True}
with (ROOT/'STOP_REQUEST.json').open('x') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
os.kill(child['pid'],signal.SIGTERM)
print({'collector_stopped':child['pid'],'owner_retained':parent['pid'],'all_connection_errors':len(calls)})
