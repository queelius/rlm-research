"""Actual CPU endpoint qualification and immutable readout closure; no GPU."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import study as s

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not s.READY.exists()
    # HF qualification belongs to PEFT Python; the actual service imports belong to native Python.
    completed=subprocess.run([str(s.train.PYTHON),'-c','import json,study;print(json.dumps(study.checkpoint()))'],
        cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,check=True,timeout=120)
    qualification=json.loads(completed.stdout)
    def write_same(path,value):
        if path.exists():assert s.read(path)==value,'partial immutable artifact changed: '+str(path)
        else:s.write_x(path,value)
    write_same(s.ROOT/'CHECKPOINT_QUALIFICATION.json',qualification)
    write_same(s.ROOT/'BINDING.json',s.binding())
    inventory=[dict(call=c,request=s.request_for(c),prompt=s.prompt(c)) for c in s.calls()]
    assert len(inventory)==72
    for row in inventory:
        c=row['call'];original=s.task(c)['request'];assert {k:v for k,v in row['request'].items() if k!='model'}=={k:v for k,v in original.items() if k!='model'}
        assert len(row['request']['token_ids'])+384<=8192
        assert set(r['implementation_id'] for r in s.child(c)['stage']['tables']['implementations'])==set(s.task(c)['known_ids'])
    write_same(s.ROOT/'INPUTS.json',dict(calls=inventory,gold_used=False,frozen_source_tasks_sha256=s.sha(s.TRAIN/'EVAL_TASKS.json')))
    suite=s.dependencies();assert suite.SERVE==s.RUNTIME/'service_wrapper_v2.py'
    # Read the exact service binding fields, including config_sha256 used by the real launcher.
    model=s.binding()['models'][s.train.ALIAS]
    assert model['config_sha256']==s.sha(Path(model['path'])/'adapter_config.json')
    fixture=s.read(s.ROOT/'CPU_TESTS.json');assert fixture['returncode']==0
    closure=dict(s.read(s.train.READY)['closure_sha256']);closure[str(s.train.READY)]=s.sha(s.train.READY)
    cp=Path(qualification['checkpoint'])
    closure.update(s.read(cp/'STEP_COMMIT.json')['artifacts_sha256'])
    for p in [cp/'STEP_COMMIT.json',s.train.OUTPUT/'RESULT.json',s.train.OUTPUT/'OWNER_TERMINAL.json']:
        closure[str(p)]=s.sha(p)
    for p in (s.RUNTIME/'CPU_READY.json',s.RUNTIME/'LIFECYCLE_READY_V2.json',suite.ROOT/'MANIFEST.json'):
        manifest=s.read(p);closure[str(p)]=s.sha(p)
        for key in ('source_sha256','source_and_artifact_sha256'):closure.update(manifest.get(key,{}))
    for p in list(s.RUNTIME.glob('*.py'))+list(s.ROOT.glob('*.py'))+[s.ROOT/n for n in ('PLAN.md','RUNBOOK.md','CPU_TESTS.json','CHECKPOINT_QUALIFICATION.json','BINDING.json','INPUTS.json')]:
        closure[str(p)]=s.sha(p)
    for directory in s.ROOT.glob('cpu-fixture-*'):
        for p in directory.rglob('*'):
            if p.is_file() and not p.is_symlink():closure[str(p)]=s.sha(p)
    for p,h in closure.items():assert s.sha(p)==h,p
    ready=dict(schema='b05-BA18-eval-ready-v1',status='CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION',
        checkpoint_qualification_sha256=s.sha(s.ROOT/'CHECKPOINT_QUALIFICATION.json'),
        binding_sha256=s.sha(s.ROOT/'BINDING.json'),train_ready_sha256=s.sha(s.train.READY),
        planned_calls=72,per_split_per_arm=18,arms=['base','cp1'],splits=['train','held'],context_units_per_split=9,
        all_phases_regardless_score=True,science_seconds=600,owner_seconds=700,external_seconds=800,workers=4,
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--outer-seconds','700'],attempt=str(s.ATTEMPT),
        actual_service_wrapper=str(suite.SERVE),native_python=str(s.NATIVE),qualification_python=str(s.train.PYTHON),
        actual_sources={p.name:s.sha(p) for p in s.ROOT.glob('*.py')},closure_sha256=dict(sorted(closure.items())))
    ready['identity']=s.digest(ready);s.write_x(s.READY,ready)
    import owner
    try:owner.execute(700)
    except ValueError as e:assert str(e)=='MAIN-owned exclusive GPU and private credential required'
    else:raise AssertionError('actual owner did not stop at CPU guard')
    assert not s.ATTEMPT.exists()
    proof=dict(status='PASS',ready_sha256=s.sha(s.READY),identity=ready['identity'],closure_pins=len(closure),
        actual_checkpoint_full_qualification=True,actual_owner_unmocked_verify_to_CPU_guard=True,GPU_calls=0)
    s.write_x(s.ROOT/'ENTRY_PROOF.json',proof);print(json.dumps(proof))

if __name__=='__main__':main()
