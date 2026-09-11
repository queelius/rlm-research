"""Seal stable sources first; publish final READY only after completed CPU qualification."""
import argparse
import json
from datetime import datetime,timezone

import campaign_common as c
from prepare import BRIEF


def seal():
    c.authenticate(c.PINS)
    old=c.read(c.OLD/'CAMPAIGN.json')
    c.authenticate(old['source_sha256']);c.authenticate(old['input_sha256'])
    source={**old['source_sha256'],**{str(p):h for p,h in c.PINS.items()}}
    data=c.read(c.DATA/'MANIFEST.json')
    source.update(data['source_sha256']);source.update(data['files_sha256'])
    for p in [*c.ROOT.glob('*.py'),*c.ROOT.glob('*.md'),BRIEF]: source[str(p)]=c.file_hash(p)
    inputs={str(p):c.file_hash(p) for p in [*sorted((c.ROOT/'inputs').glob('*.json')),c.ROOT/'RECIPE.json',c.ROOT/'CPU_TESTS.json']}
    manifest={'schema':c.ROOT.name,'namespace':c.ROOT.name,'seed':c.SEED,'source_sha256':source,'input_sha256':inputs,
        'initial_policy':c.original_policy(),'fixed_child_sha256':c.CHILD_SHA,'inherited_updates':0,
        'validation_selection':'fixed-final16 primary; earliest max validation descriptive only',
        'training_episodes':384,'validation_episodes':80,'transfer_episodes':96,'gpu_calls_during_preparation':0}
    manifest['campaign_id']=c.digest(manifest)
    c.write_once(c.ROOT/'CAMPAIGN.json',manifest)
    amendment={'schema':'broad16-original-start-exclusion-only-v1','namespace':c.ROOT.name,
        'source_sha256':source,'input_sha256':inputs,'inherited_optimizer_steps':0,'new_global_cap_seconds':18120,
        'admission_change':'none; same authenticated unsampled-child-overflow exclusion only',
        'lifecycle_change':'reuse observed vanished-process absence fix; no other process semantics change'}
    amendment['amendment_id']=c.digest(amendment);c.write_once(c.ROOT/'AMENDMENT.json',amendment)
    life={'schema':'private-rebinding-lifecycle-v2-with-observed-process-exit-fix','source_sha256':source,
        'new_campaign_sha256':c.file_hash(c.ROOT/'CAMPAIGN.json')}
    life['amendment_id']=c.digest(life);c.write_once(c.ROOT/'LIFECYCLE_V2.json',life)
    c.write_once(c.ROOT/'PREPARED.json',{'status':'sources_and_inputs_frozen_pending_CPU_native_qualification',
        'campaign_sha256':c.file_hash(c.ROOT/'CAMPAIGN.json'),'campaign_id':manifest['campaign_id']})
    return {'campaign_id':manifest['campaign_id'],'sources_frozen':True,'READY_published':False}


def ready():
    campaign=c.verify_campaign();proof=c.read(c.ROOT/'qualification/RESULT.json')
    if proof['rootless_fixture']['credited_root_calls']!=2 or proof['rootless_fixture']['uncredited_child_calls']!=1:
        raise ValueError('actual trusted CPU native qualification missing')
    own=[c.ROOT/n for n in ['CAMPAIGN.json','AMENDMENT.json','LIFECYCLE_V2.json','PREPARED.json']]
    own.append(c.ROOT/'IMPLEMENTATION_REPORT.md')
    own += [c.ROOT/'qualification.stdout.log',c.ROOT/'qualification.stderr.log']
    own += [p for p in (c.ROOT/'qualification').rglob('*') if p.is_file() and p.suffix in ('.json',)]
    value={'status':'CPU_READY_BROAD16_FIXED_FINAL','published_utc':datetime.now(timezone.utc).isoformat(),
        'campaign_sha256':c.file_hash(c.ROOT/'CAMPAIGN.json'),'campaign_id':campaign['campaign_id'],
        'source_sha256':{**campaign['source_sha256'],**campaign['input_sha256'],**{str(p):c.file_hash(p) for p in own}},
        'argv':[str(c.NATIVE_PYTHON),str(c.ROOT/'campaign.py'),'run'],
        'verify_argv':[str(c.NATIVE_PYTHON),str(c.ROOT/'campaign.py'),'verify'],
        'cwd':str(c.ROOT),'output':str(c.ROOT/'outputs/attempt-001'),
        'work_cap_seconds':18000,'inclusive_exception_cap_seconds':18120,'parent_outer_cap_seconds':18150,
        'gpu_shape':'one exclusively assigned A100; inherited CUDA_VISIBLE_DEVICES and LD environment; no hardcoded physical ordinal',
        'parent_acceptance_and_launch_required':True,'automatic_retry':False,'gpu_calls_during_preparation':0,
        'dynamic_dependency':'first actual fresh collection supplies native physical action masks/logprobs; CPU synthetic fixtures never train the research model',
        'primary_policy':'fixed-final16, never validation-selected substitute','qualification':proof}
    c.write_once(c.ROOT/'READY.json',value)
    return {'ready_sha256':c.file_hash(c.ROOT/'READY.json'),'campaign_id':campaign['campaign_id']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['seal','ready']);args=parser.parse_args()
    print(json.dumps(seal() if args.command=='seal' else ready()))
