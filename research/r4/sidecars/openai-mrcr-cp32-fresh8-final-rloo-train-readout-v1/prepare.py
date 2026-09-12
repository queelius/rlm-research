"""Pin actual trained endpoint and original complete cp32 control; CPU only."""
import os
import checkpoint
import study

def prepare():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not study.READY.exists()
    q=checkpoint.verify_checkpoint();assert q==study.read(study.PRIOR/'CHECKPOINT_QUALIFICATION.json')
    assert study.read(study.ROOT/'CPU_TESTS.json')['returncode']==0
    pins={}
    for p in (study.PRIOR/'READY.json',study.SCREEN/'READY.json'):
        r=study.read(p);assert r['identity']==study.digest({k:v for k,v in r.items() if k!='identity'})
        pins.update(r['closure_sha256']);pins[str(p)]=study.sha(p)
    terminal=study.read(study.BASELINE/'OWNER_TERMINAL.json')
    result=study.read(study.BASELINE/'science/RESULT.json')
    assert terminal['complete'] and terminal['released'] and not terminal.get('errors')
    assert result['complete'] and result['planned']==result['recorded']==32
    assert result['scientifically_available']==32 and result['child_actions']==0
    assert all(result[k] for k in ('all_causal_mappings_complete','all_initial_root_prefixes_verified','all_action_caps_respected'))
    assert study.read(study.BASELINE/'science/TERMINAL_STRIP_CONTRACT.json')['condition']=='terminal-strip-disabled'
    assert study.read(study.BASELINE/'owned-service/BINDING.json')==study.read(study.TRAINING/'PARENT_BINDING.json')
    plan=study.schedule('train');assert len(plan)==32 and len({r['record_id'] for r in plan})==8
    byid={r['id']:r for r in plan}
    episodes=list((study.BASELINE/'science/episodes').glob('*.json'));assert len(episodes)==32
    for p in episodes:
        row=study.read(p);assert row['coordinate']==byid[row['coordinate']['id']]
        assert study.digest(row['episode'])==row['episode_sha256']
    for root in (checkpoint.OUTPUT,study.BASELINE/'science',study.input_dir('train')):
        for p in root.rglob('*'):
            if p.is_file():pins[str(p)]=study.sha(p)
    for name in ('OWNER_RUN.json','OWNER_TERMINAL.json','owned-service/BINDING.json','owned-service/PREFLIGHT.json'):
        p=study.BASELINE/name;pins[str(p)]=study.sha(p)
    study.write_x(study.ROOT/'CHECKPOINT_QUALIFICATION.json',q)
    for p in study.ROOT.iterdir():
        if p.is_file():pins[str(p)]=study.sha(p)
    for p,h in pins.items():assert study.sha(p)==h,p
    ready=dict(schema='fresh8-rloo-in-sample-readout-ready-v1',closure_sha256=pins,
        inputs={'train':dict(planned=32,unique_contexts=8,schedule_sha256=study.digest(plan),input_dir=str(study.input_dir('train')))},
        control=dict(output=str(study.BASELINE),available=result['scientifically_available'],raw_exact=result['raw_exact'],
                     result_sha256=study.sha(study.BASELINE/'science/RESULT.json'),new_control_queries=0),
        checkpoint_qualification=q,planned=32,temperature=.5,max_action_tokens=2048,total_actions=6,children=0,workers=4,
        fixed_argv={'train':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--phase','train']},caps=study.CAPS,
        evaluation_exposure='same original training examples/actions seeds; in-sample diagnostic only',
        all32_regardless_source_advantage=True,no_outcome_manipulation_gate=True,
        legacy_manipulation_gate_field_inapplicable=True,endpoint_selection=False,optimizer_steps=0,GPU_admission=False)
    ready['identity']=study.digest(ready);study.write_x(study.READY,ready)
    study.verify();print(dict(identity=ready['identity'],ready_sha256=study.sha(study.READY),pins=len(pins)))

if __name__=='__main__':prepare()
