"""CPU-only exact schedule seal and actual owner entry guard; no service/model."""
import json
import os
from pathlib import Path
import sys
import importlib.metadata
import owner
import study

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not study.READY_RUN.exists()
    assert study.sha(study.DATA/'CANDIDATE_MANIFEST.json')==study.DATA_SHA
    manifest=study.read(study.DATA/'CANDIDATE_MANIFEST.json')
    parent=study.IDS/'READY_RUN.json';parent_ready=study.read(parent)
    closure=dict(parent_ready['closure_sha256']);closure[str(parent)]=study.sha(parent)
    for kind in ('source_sha256','artifacts_sha256'):closure.update(manifest[kind])
    for path in (study.DATA/'CANDIDATE_MANIFEST.json',study.DATA/'DESIGN.md'):
        closure[str(path)]=study.sha(path)
    for path,expected in closure.items():assert study.sha(Path(path))==expected,path
    inventory=[]
    bounds={(r['root_id'],r['helpers'],p['part']):p for r in study.read(study.DATA/'TOKEN_INVENTORY.json')['rows'] for p in r['members']}
    for call in study.calls():
        prompt=study.prompt(call);request=study.request_body(prompt,call['seed'],call['max_tokens'])
        bound=bounds[call['root_id'],call['helpers'],call['part']]
        assert study.digest(request['token_ids'])==bound['prefix_sha256']
        assert len(request['token_ids'])==bound['input_tokens']
        assert bound['all_assigned_ID_output_tokens_including_EOS']<=call['max_tokens']
        assert request==study.request_body(study.b05().render(study.source.b05().render_child(study.child(call))),call['seed'],call['max_tokens'])
        inventory.append(dict(call=call,call_id=study.call_id(call),prompt=prompt,request=request,
            prefix_token_ids_sha256=study.digest(request['token_ids']),
            assigned_IDs=bound['assigned_ids'],all_known_ID_payload_tokens=bound['all_assigned_ID_output_tokens_including_EOS']))
    study.write_x(study.ROOT/'INPUTS.json',dict(schema='b05-width-frozen-native-inputs-v1',calls=inventory,gold_in_model_inputs=False))
    assert study.read(study.ROOT/'CPU_TESTS.json')['returncode']==0
    for path in list(study.ROOT.glob('*.py'))+[study.ROOT/n for n in ('RUNBOOK.md','PLAN.md','INPUTS.json','CPU_TESTS.json')]:
        closure[str(path)]=study.sha(path)
    for path in (study.ROOT/'cpu-fixture-001').rglob('*'):
        if path.is_file() and not path.is_symlink():closure[str(path)]=study.sha(path)
    ready=dict(schema='b05-helper-width-ready-v1',status='CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION',
        candidate_manifest_sha256=study.DATA_SHA,parent_ready_sha256=study.sha(parent),
        attempt=str(study.ATTEMPT),planned_calls=126,stage_policy_outputs=54,cases=9,
        width_cases={'6':3,'12':3,'20':3},helpers=[1,2,4],repeats=2,root_model_calls=0,
        science_seconds=600,owner_seconds=700,external_seconds=800,workers=4,total_stage_output_cap=384,
        argv=[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--outer-seconds','700'],
        python=sys.version,packages={n:importlib.metadata.version(n) for n in ('torch','transformers','vllm','renderers')},
        unchanged_native_runtime_and_ID_contract=True,no_eligibility_repair=True,no_gold_partition=True,
        all_conditions_outcome_independent=True,fixed_not_learned_depth=True,
        primary='stage eligible-ID-set exact with invalid/unavailable separate; strict-valid precision/recall',
        actual_source_files={p.name:study.sha(p) for p in sorted(study.ROOT.glob('*.py'))},
        launch_authority='MAIN only',closure_sha256=dict(sorted(closure.items())))
    ready['identity']=study.digest(ready);study.write_x(study.READY_RUN,ready)
    # Enter the actual inherited execute function with full unmocked verification.
    try:owner.implementation().execute(700)
    except ValueError as error:
        assert str(error)=='MAIN-owned exclusive GPU and private credential required'
    else:raise AssertionError('CPU guard did not reject')
    assert not study.ATTEMPT.exists()
    receipt=dict(status='PASS',ready_sha256=study.sha(study.READY_RUN),identity=ready['identity'],
        actual_execute_after_unmocked_verify=True,stopped_at='exclusive GPU/private credential guard',
        attempt_absent=True,GPU_calls=0,pins=len(closure))
    study.write_x(study.ROOT/'ENTRY_PROOF.json',receipt)
    print(json.dumps(receipt))

if __name__=='__main__':main()
