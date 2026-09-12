"""Stop the identified all-connection-error collector; leave owner to release service."""
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

parent=observe(781910);child=observe(782667)
assert parent['uid']==child['uid']==os.getuid()==1523821556
assert child['ppid']==parent['pid'] and child['pgid']==child['pid']
assert parent['argv']==[NATIVE,str(SIDE/'owner.py'),'run','--output',str(SIDE/'outputs/attempt-001'),'--outer-seconds','1100']
assert child['argv']==[NATIVE,str(SIDE/'collect.py'),'--phase','train','--arm','checkpoint32','--endpoint',str(SIDE/'outputs/attempt-001/owned-service/service/endpoint-original.json'),'--output',str(SIDE/'outputs/attempt-001/science'),'--deadline','1789245967.4026504']
calls=[json.loads(p.read_text()) for p in (SIDE/'outputs/attempt-001/science/native-calls').glob('*-result.json')]
assert len(calls)>=217 and all(c['status']=='error' and c['error']['type']=='ProviderError' and c['error']['message']=='Connection error.' for c in calls)
receipt={'epoch':time.time(),'authority':'MAIN','signal':'SIGTERM','target':child,'authenticated_owner':parent,
         'owner_retained_for_release':True,'observed_calls':len(calls),'returned_calls':0,
         'reason':'All native attempts fail connection before any scientific model return. Stop uninformative transport retries; diagnose CPU while accepted cp16/flexible jobs use GPU.',
         'no_files_deleted':True,'original_outcomes_unchanged':True}
with (ROOT/'STOP_REQUEST.json').open('x') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
os.kill(child['pid'],signal.SIGTERM)
print({'collector_stopped':child['pid'],'owner_retained':parent['pid'],'all_connection_errors':len(calls)})
