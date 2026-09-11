"""Complete frozen24 admission; unchanged native root-only TIS/Adam numerics."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import traceback
import uuid
import qsr_study as s
from qsr_common import c,starting_decision
SOURCE=s.CAMPAIGN/'campaign_train.py'
with s.aliases({'campaign_common':c}):impl=s.load('qsr_qualified_numerics',SOURCE,s.PINS[SOURCE])

def check_members(rows,plans,generation):
    expected={r['id']:r for r in plans}
    if len(rows)!=24 or len(expected)!=24 or len({r['episode_id'] for r in rows})!=24:raise ValueError('complete distinct24 required')
    for row in rows:
        if row['coordinate']!=expected.get(row['episode_id']) or row['split']!='training' or row.get('qualification_only') is not False or row.get('generation_id')!=generation['generation_id']:raise ValueError('foreign, stale, qualification or nontraining coordinate')

def authenticate_group(group_path,generation_path):
    campaign=s.verify_prepared();starting_decision();generation=s.read(generation_path);group=s.read(group_path);policy=generation['previous_policy']
    c.check_generation(generation,policy,policy['step']);c.authenticate_policy(policy)
    if generation['campaign_id']!=campaign['campaign_id'] or group['generation']!=generation:raise ValueError('foreign/stale group generation')
    plans=s.candidate_plan(generation['candidate_window'])
    if generation['coordinate_plan_sha256']!=s.digest(plans):raise ValueError('not frozen24 window')
    manifest=s.read(group_path.parent/'MANIFEST.json')
    if manifest['planned']!=24 or manifest['recorded']!=24 or not manifest['complete'] or manifest['integrity_failures'] or manifest['generation']!=generation:raise ValueError('complete clean24 export required')
    for name,pin in manifest['artifact_sha256'].items():s.check(group_path.parent/name,pin)
    if group_path.name not in manifest['artifact_sha256']:raise ValueError('unbound group')
    rows=s.read(group_path.parent/'EPISODES.json');check_members(rows,plans,generation)
    helper=c.pilot_math();rebuilt=helper.recompute_group(rows)
    for key in ('dataset_id','role_binding','generation','credit_policy'):rebuilt[key]=group[key]
    rebuilt['group_id']=s.digest({k:v for k,v in rebuilt.items() if k!='group_id'})
    if rebuilt!=group:raise ValueError('mixed-group selection or advantages changed')
    binding=group['role_binding'];alias=binding['role_map']['root']
    if binding['campaign_policy']!=policy or binding['models'][binding['fixed_child']]['adapter_sha256']!=s.CHILD_SHA:raise ValueError('policy/child binding changed')
    for row in group['episodes']:
        for turn in row['turns']:
            helper.validate_root_turn(turn,alias,policy['adapter_sha256'],8192)
            if turn.get('typed_wire_grammar') is not False:raise ValueError('root has constrained likelihood')
            audit=turn['role_audit'];s.check(audit['source_audit_path'],audit['source_audit_sha256']);s.check(turn['typed_audit_path'],turn['typed_audit_sha256'])
        if any(t['credited'] for t in row['all_role_evidence'] if t['role_depth']!=0):raise ValueError('child credited')
    command=[str(s.NATIVE),str(s.ROOT/'qsr_native.py'),'verify-export','--output',str(group_path.parent)]
    result=subprocess.run(command,check=True,text=True,capture_output=True,timeout=180,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    proof=json.loads(result.stdout)
    if proof['group_sha256']!=s.sha(group_path) or proof['replayed']!=24:raise ValueError('native source replay differs')
    recipe=s.read(s.ROOT/'RECIPE.json');base=Path(recipe['base_model']);s.check(base/'local-research-manifest.json',recipe['base_manifest_sha256'])
    for path,pin in s.read(base/'local-research-manifest.json')['files'].items():s.check(base/path,pin)
    identity=dict(generation=generation,generation_file_sha256=s.sha(generation_path),group_path=str(group_path),group_sha256=s.sha(group_path),group_id=group['group_id'],export_manifest_sha256=s.sha(group_path.parent/'MANIFEST.json'),native_replay=proof,campaign_sha256=s.sha(s.ROOT/'CAMPAIGN.json'),recipe_sha256=s.sha(s.ROOT/'RECIPE.json'),role_binding=binding,child_loaded_into_training_model=False,candidate_window=generation['candidate_window'],replay_argv=command)
    identity['input_identity']=s.digest(identity);return group,generation,identity
impl.authenticate_group=authenticate_group
def parse_args(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--group',type=Path,required=True);p.add_argument('--generation',type=Path,required=True);p.add_argument('--output',type=Path);p.add_argument('--deadline',type=float,default=float('inf'));p.add_argument('--preflight',action='store_true');return p.parse_args(argv)
if __name__=='__main__':
    a=parse_args()
    try:print(json.dumps(impl.train(a),sort_keys=True,allow_nan=False))
    except BaseException as error:
        if a.output is not None:s.write(a.output.parent/('TRAIN_FAILURE-'+uuid.uuid4().hex+'.json'),dict(type=type(error).__name__,error=str(error),traceback=traceback.format_exc(),checkpoint_preserved=True))
        raise
