"""Eight-slot native groups share one immutable full-window policy generation."""
import argparse
import asyncio
import functools
import re
from pathlib import Path
import common
import native as n
import study as s

impl=s.private('collect.py',{'study':s,'native':n,'common':common})
binding_for=impl.binding_for
validate_descriptor=impl.validate_descriptor

def group_phase(phase):
    m=re.fullmatch(r'window-([1-4])-group-([1-4])',phase)
    if not m:raise ValueError('not a frozen candidate-group phase')
    return tuple(map(int,m.groups()))

def planned(phase):
    plans=s.read(s.ROOT/'inputs/PLANS.json')
    if phase in ('readout-before','readout-after'):return plans['readout']
    window,group=group_phase(phase)
    return plans['windows'][str(window)][group-1]

@functools.lru_cache(maxsize=None)
def verify_spec(path):
    campaign=s.verify_prepared();spec=s.read(path)
    if (spec['schema']!=s.ROOT.name or spec['scientific'] is not True
        or spec['campaign_sha256']!=s.sha(s.ROOT/'CAMPAIGN.json')
        or spec['plan']!=planned(spec['phase']) or spec['workers']!=4
        or spec['environment']!=n.stack().interface.e.environment_config()
        or spec['runtime_ready_sha256']!=s.PINS[s.LOCAL/'READY.json']):
        raise ValueError('capture differs from frozen refill campaign')
    s.check(spec['binding_path'],spec['binding_sha256']);s.check(spec['endpoint_path'],spec['endpoint_sha256'])
    binding,descriptor=spec['binding'],spec['descriptor']
    if binding!=s.read(spec['binding_path']) or descriptor!=s.read(spec['endpoint_path']) or binding!=binding_for(binding['campaign_policy']):
        raise ValueError('current policy/endpoint binding differs')
    validate_descriptor(binding,descriptor,spec['binding_sha256'],s.read(s.ROOT/'RECIPE.json')['base_manifest_sha256'])
    n.stack().native.e.capture.recursive.validate_serving_evidence(spec['serving_evidence'])
    g=spec['generation']
    if spec['phase'].startswith('window-'):
        window,_=group_phase(spec['phase']);policy=binding['campaign_policy']
        if g is None:raise ValueError('training group lacks generation')
        common.c.check_generation(g,policy,policy['step'])
        if g['candidate_window']!=window or g['campaign_id']!=campaign['campaign_id'] or g['coordinate_plan_sha256']!=s.digest(s.candidate_plan(window)):
            raise ValueError('stale policy/window or changed full candidate plan')
    elif g is not None:raise ValueError('readout cannot carry training generation')
    return spec

impl.planned=planned;impl.verify_spec=verify_spec
prepare_spec=impl.prepare_spec;dispatch=impl.dispatch;collect=impl.collect

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);a=p.parse_args()
    raise SystemExit(asyncio.run(collect(a.spec,a.output,a.deadline)))
