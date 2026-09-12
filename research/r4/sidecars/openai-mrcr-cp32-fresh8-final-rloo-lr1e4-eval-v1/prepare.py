"""Seal the actual fixed new endpoint and four already-qualified saved controls."""
import os
import checkpoint
import study

def prepare():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not study.READY.exists()
    q=checkpoint.verify_checkpoint();assert q['learning_rate']==1e-4
    assert study.read(study.ROOT/'CPU_TESTS.json')['returncode']==0
    pins={};controls={};inputs={}
    for p in (study.train.READY,study.PRIOR/'READY.json',study.TRAINREAD/'READY.json'):
        r=study.read(p);assert r['identity']==study.digest({k:v for k,v in r.items() if k!='identity'})
        pins.update(r['closure_sha256']);pins[str(p)]=study.sha(p)
    for p in checkpoint.OUTPUT.rglob('*'):
        if p.is_file():pins[str(p)]=study.sha(p)
    expected_cp32=study.read(study.TRAINING/'PARENT_BINDING.json')
    expected_lr1e5=study.read(study.prior.train.OUTPUT/'checkpoint-0001/EVAL_BINDING.json')
    for phase in study.CAPS:
        plan=study.schedule(phase);assert len(plan)==32;byid={r['id']:r for r in plan}
        inputs[phase]=dict(planned=32,unique_contexts=len({r['record_id'] for r in plan}),
                          schedule_sha256=study.digest(plan),input_dir=str(study.input_dir(phase)))
        controls[phase]={}
        for name,source in study.CONTROLS[phase].items():
            terminal=study.read(source/'OWNER_TERMINAL.json');r=study.read(source/'science/RESULT.json')
            assert terminal['complete'] and terminal['released'] and not terminal.get('errors')
            assert r['complete'] and r['planned']==r['recorded']==r['scientifically_available']==32
            assert all(r[k] for k in ('all_causal_mappings_complete','all_initial_root_prefixes_verified','all_action_caps_respected'))
            assert r['child_actions']==0
            assert study.read(source/'science/TERMINAL_STRIP_CONTRACT.json')['condition']=='terminal-strip-disabled'
            assert study.read(source/'owned-service/BINDING.json')==(expected_cp32 if name=='cp32' else expected_lr1e5)
            episodes=list((source/'science/episodes').glob('*.json'));assert len(episodes)==32
            for p in episodes:
                item=study.read(p);assert item['coordinate']==byid[item['coordinate']['id']]
                assert study.digest(item['episode'])==item['episode_sha256']
            for p in (source/'science').rglob('*'):
                if p.is_file():pins[str(p)]=study.sha(p)
            for name2 in ('OWNER_RUN.json','OWNER_TERMINAL.json','owned-service/BINDING.json','owned-service/PREFLIGHT.json'):
                p=source/name2;pins[str(p)]=study.sha(p)
            controls[phase][name]=dict(output=str(source),result_sha256=study.sha(source/'science/RESULT.json'),
                                      available=r['scientifically_available'],correct=r['raw_exact'],new_control_queries=0)
    study.write_x(study.ROOT/'CHECKPOINT_QUALIFICATION.json',q)
    for p in study.ROOT.iterdir():
        if p.is_file():pins[str(p)]=study.sha(p)
    for p,h in pins.items():assert study.sha(p)==h,p
    ready=dict(schema='fresh8-rloo-LR10x-two-panel-eval-ready-v1',closure_sha256=pins,
        checkpoint_qualification=q,inputs=inputs,controls=controls,planned_new_outputs=64,
        caps=study.CAPS,fixed_argv={p:[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--phase',p] for p in study.CAPS},
        temperature=.5,max_action_tokens=2048,total_actions=6,children=0,workers=4,
        phases_regardless_score=True,no_outcome_manipulation_gate=True,legacy_train_gate_inapplicable=True,
        endpoint_selection=False,optimizer_steps=0,GPU_admission=False)
    ready['identity']=study.digest(ready);study.write_x(study.READY,ready);study.verify()
    print(dict(identity=ready['identity'],ready_sha256=study.sha(study.READY),pins=len(pins)))

if __name__=='__main__':prepare()
