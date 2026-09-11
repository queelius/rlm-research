"""Exact consumed-prefix admission around unchanged root-only TIS/Adam/checkpoint math."""
import argparse
import json
import os
import subprocess
import traceback
import uuid
from pathlib import Path
import study as s
from common import c,starting_decision

SOURCE=s.CAMPAIGN/'campaign_train.py'
with s.aliases({'campaign_common':c}):impl=s.load('refill_numerics',SOURCE,s.PINS[SOURCE])

def authenticate_group(group_path,generation_path):
    campaign=s.verify_prepared();starting_decision()
    generation,group=s.read(generation_path),s.read(group_path);policy=generation['previous_policy']
    c.check_generation(generation,policy,policy['step']);c.authenticate_policy(policy)
    if generation['campaign_id']!=campaign['campaign_id'] or group['generation']!=generation:
        raise ValueError('stale group generation or foreign campaign')
    plans=s.candidate_plan(generation['candidate_window'])
    if generation['coordinate_plan_sha256']!=s.digest(plans):raise ValueError('not the frozen full32 window')
    manifest=s.read(group_path.parent/'MANIFEST.json')
    if manifest.get('schema')!='refill-window-union-v1' or manifest['decision']!='update' or manifest['generation']!=generation:
        raise ValueError('only complete mixed consumed-window export is trainable')
    for name,want in manifest['artifact_sha256'].items():s.check(group_path.parent/name,want)
    count=manifest['consumed_groups']
    if count not in (2,3,4) or manifest['recorded']!=8*count or manifest['planned']!=8*count or manifest['integrity_failures']:
        raise ValueError('invalid consumed-prefix cardinality or native integrity')
    if group_path.name not in manifest['artifact_sha256']:raise ValueError('unbound training group')
    rows=s.read(group_path.parent/'EPISODES.json');expected={r['id']:r for r in plans[:8*count]}
    if len(rows)!=len(expected) or len({r['episode_id'] for r in rows})!=len(rows):raise ValueError('missing/duplicate consumed prefix')
    for row in rows:
        if (row['coordinate']!=expected.get(row['episode_id']) or row['split']!='training'
            or row.get('qualification_only') is not False or row.get('generation_id')!=generation['generation_id']):
            raise ValueError('nontraining, qualification or stale likelihood')
    helper=c.pilot_math();rebuilt=helper.recompute_group(rows)
    for key in ('dataset_id','role_binding','generation','credit_policy'):rebuilt[key]=group[key]
    rebuilt['group_id']=s.digest({k:v for k,v in rebuilt.items() if k!='group_id'})
    if rebuilt!=group:raise ValueError('mixed membership/advantage changed')
    binding=group['role_binding'];alias=binding['role_map']['root']
    if binding['campaign_policy']!=policy or binding['models'][binding['fixed_child']]['adapter_sha256']!=c.CHILD_SHA:
        raise ValueError('root/current-policy or fixed child differs')
    recipe=s.read(s.ROOT/'RECIPE.json')
    for row in group['episodes']:
        for turn in row['turns']:
            helper.validate_root_turn(turn,alias,policy['adapter_sha256'],recipe['max_causal_tokens'])
            if turn.get('typed_wire_grammar') is not False:raise ValueError('grammar-constrained root cannot supply unrestricted likelihood')
            audit=turn['role_audit'];s.check(audit['source_audit_path'],audit['source_audit_sha256'])
            s.check(turn['typed_audit_path'],turn['typed_audit_sha256'])
        if any(t['credited'] for t in row['all_role_evidence'] if t['role_depth']!=0):raise ValueError('child credited')
    # Native renderer/graph parser remains in its qualified environment, separate
    # from training. This replays actual immutable evidence, not synthetic logps.
    result=subprocess.run([str(s.NATIVE),str(s.ROOT/'native.py'),'verify-export','--output',str(group_path.parent)],
        check=True,text=True,capture_output=True,timeout=180,
        env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    proof=json.loads(result.stdout)
    if proof['group_sha256']!=s.sha(group_path) or proof['replayed']!=8*count:raise ValueError('native proof differs from consumed union')
    base=Path(recipe['base_model']);s.check(base/'local-research-manifest.json',recipe['base_manifest_sha256'])
    for path,want in s.read(base/'local-research-manifest.json')['files'].items():s.check(base/path,want)
    identity={'generation':generation,'generation_file_sha256':s.sha(generation_path),
        'group_path':str(group_path),'group_sha256':s.sha(group_path),'group_id':group['group_id'],
        'export_manifest_sha256':s.sha(group_path.parent/'MANIFEST.json'),'native_replay':proof,
        'campaign_sha256':s.sha(s.ROOT/'CAMPAIGN.json'),'recipe_sha256':s.sha(s.ROOT/'RECIPE.json'),
        'role_binding':binding,'child_loaded_into_training_model':False,
        'candidate_window':generation['candidate_window'],'consumed_groups':count}
    identity['input_identity']=s.digest(identity)
    return group,generation,identity

impl.authenticate_group=authenticate_group

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--group',type=Path,required=True);p.add_argument('--generation',type=Path,required=True)
    p.add_argument('--output',type=Path);p.add_argument('--deadline',type=float,default=float('inf'));p.add_argument('--preflight',action='store_true');a=p.parse_args()
    try:print(json.dumps(impl.train(a),sort_keys=True,allow_nan=False))
    except BaseException as error:
        if a.output is not None:s.write(a.output.parent/('TRAIN_FAILURE-'+uuid.uuid4().hex+'.json'),{'type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc(),'checkpoint_preserved':True})
        raise
