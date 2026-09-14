"""Start or resume the finite campaign independently of the Codex process."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import time
import uuid
import psutil

ROOT=Path(__file__).resolve().parent
PYTHON='/project/alex_phd/envs/prime-rl-5990b1b/bin/python'

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--resume',action='store_true'); args=parser.parse_args()
    pilot=ROOT/'outputs/pilot-003'
    status=json.loads((pilot/'STATUS.json').read_text())
    assert status['state']=='finished' and not status['failures']
    calls=[json.loads(p.read_text()) for p in pilot.glob('models/*/calls/*.json')]
    assert len(calls)>=20 and all(c['available'] for c in calls)
    assert list(pilot.glob('services/*/RELEASED.json'))
    output=ROOT/'outputs/campaign-001'
    if output.exists() and not args.resume: raise RuntimeError('existing campaign; use --resume deliberately')
    if (output/'STOP').exists(): raise RuntimeError('intentional STOP marker still exists')
    if (ROOT/'LAUNCH.json').exists():
        prior=json.loads((ROOT/'LAUNCH.json').read_text())
        try:
            process=psutil.Process(prior['pid'])
            if process.create_time()==prior['create_time'] and process.status()!=psutil.STATUS_ZOMBIE:
                raise RuntimeError('previous detached owner still running')
        except psutil.NoSuchProcess: pass
    deadline=min(time.time()+36*3600,int(os.environ.get('SLURM_JOB_END_TIME','1789493416'))-600)
    seconds=int(deadline-time.time())
    assert seconds>300
    identifier=uuid.uuid4().hex[:12]
    command=['timeout','--signal=TERM','--kill-after=120',str(seconds),PYTHON,str(ROOT/'campaign_v3.py'),
        '--output',str(output),'--hours','36']
    log=ROOT/f'detached-{identifier}.log'
    with log.open('x') as stream:
        process=subprocess.Popen(command,cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},
            stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    receipt={'pid':process.pid,'create_time':psutil.Process(process.pid).create_time(),'started':time.time(),
        'deadline':deadline,'command':command,'log':str(log),'output':str(output),
        'python':PYTHON,'packages':{p:importlib.metadata.version(p) for p in ('torch','vllm','transformers','psutil')}}
    receipt_path=ROOT/('LAUNCH-'+identifier+'.json' if args.resume else 'LAUNCH.json')
    with receipt_path.open('x') as stream: json.dump(receipt,stream,indent=2)
    print(json.dumps(receipt,indent=2))
