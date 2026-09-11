"""Approved16-round state machine adaptation; primary fixed-final16, never test selection."""
import argparse
import fcntl
import json
import os
import signal
import sys
import time

import campaign_common as c

sys.modules['campaign'] = sys.modules[__name__]


def fixed_final_selection(policies, validations):
    if 16 not in policies or [v['step'] for v in validations] != [0,4,8,12,16]:
        raise ValueError('complete final16 and all prespecified validation stages required')
    if any(v['planned'] != 16 for v in validations):
        raise ValueError('validation denominator must remain16')
    descriptive = min(validations,key=lambda v:(-v['strict_successes'],v['step']))['step']
    return {'policy':policies[16],'selected_step':16,'primary_fixed_final_step':16,
        'descriptive_earliest_max_validation_step':descriptive,'validation':validations,
        'rule':'fixed-final16; earliest validation maximum is descriptive only; transfer never selects weights'}


impl = c.adapted('broad_private_coordinator',c.OLD/'campaign.py',[
    ('four-hour global envelope','five-hour work envelope',1),
    ('while max(policies) <= 8:','while max(policies) <= 16:',1),
    ('step in (0, 2, 4, 6, 8)','step in (0, 4, 8, 12, 16)',2),
    ('step < 8','step < 16',2),
    ('if step == 8:','if step == 16:',1),
    ('"planned": 8,','"planned": 16,',1),
    ('selected = min(validations, key=lambda row: (-row["strict_successes"], row["step"]))["step"]\n        selection = {"policy": policies[selected], "selected_step": selected, "validation": validations,\n                     "rule": "earliest maximum strict successes over fixed8; excluded failures reported separately"}',
     'selected = 16\n        selection = fixed_final_selection(policies, validations)',1),
    ('("selected", policies[selected])','("final", policies[selected])',1),
    ('"final_policy": policies[8]','"final_policy": policies[16]',1),
    ('("original", "selected")','("original", "final")',1)],
    {'fixed_final_selection':fixed_final_selection})
observer_fix = c.private('broad_observed_exit_fix',c.ROOT.parent/'root-seed-lifecycle-continuation-v1/driver.py')
observer_fix.install_observer_patch(sys.modules[__name__])
_life = None


def __getattr__(name):
    return getattr(impl,name)


def lifecycle():
    global _life
    if _life is None:
        _life=c.private('campaign_lifecycle_v2',c.OLD/'campaign_lifecycle_v2.py')
        _life.V1_CAMPAIGN_SHA=c.file_hash(c.ROOT/'CAMPAIGN.json')
        _life.verify_amendment()
        impl.claim_service,impl.stop_service=_life.claim_service,_life.stop_service
    return _life


def main():
    entered=time.time()
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['verify','run'])
    parser.add_argument('--output',type=c.Path,default=c.ROOT/'outputs/attempt-001')
    args=parser.parse_args()
    c.verify_campaign()
    import campaign_native as native
    native.install()
    if args.command=='verify':
        print(json.dumps({'campaign_verified':True,'initial_binding':native.binding_for(c.original_policy()),'gpu_calls':0}))
        return
    ready=c.read(c.ROOT/'READY.json')
    if ready['status']!='CPU_READY_BROAD16_FIXED_FINAL':
        raise ValueError('final CPU qualification required')
    c.authenticate(ready['source_sha256'])
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or ',' in os.environ['CUDA_VISIBLE_DEVICES'] or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('parent must assign one exclusive GPU and existing service key')
    if args.output.resolve().parent!=c.ROOT/'outputs' or args.output.exists():
        raise ValueError('new own-namespace output required; no implicit retry')
    def hard_stop(sig,frame):
        raise TimeoutError('broad16 inclusive18120-second cap or parent signal')
    for sig in (signal.SIGALRM,signal.SIGTERM,signal.SIGINT):
        signal.signal(sig,hard_stop)
    signal.setitimer(signal.ITIMER_REAL,max(.001,18120-(time.time()-entered)))
    with (c.ROOT/'COORDINATOR.lock').open('a') as lease:
        fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:
            print(json.dumps(impl.run_campaign(argparse.Namespace(output=args.output,resume=False)),sort_keys=True))
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    main()
