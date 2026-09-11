import os
from pathlib import Path
from types import SimpleNamespace
import pytest
import recovery as r

def test_actual_owner_gpu_command_and_installed_collector_environment(tmp_path,monkeypatch):
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','MIG-CPU-qualification-exact-assignment')
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU_FIXTURE_NOT_CREDENTIAL')
    suite=r.dependencies();seen=[]
    class FakeProcess:
        pid=987654;returncode=0
        def wait(self,timeout=None):return 0
        def poll(self):return 0
    def popen(argv,**kwargs):
        seen.append((argv,kwargs['env']['CUDA_VISIBLE_DEVICES']))
        return FakeProcess()
    monkeypatch.setattr(r.subprocess,'Popen',popen)
    monkeypatch.setattr(suite.life,'observe',lambda pid:dict(pid=pid,pgid=pid,uid=os.getuid()))
    monkeypatch.setattr(suite.life,'safe_observation',lambda x:x)
    monkeypatch.setattr(suite,'stop_child',lambda *a:None)
    monkeypatch.setattr(suite,'observe_service',lambda *a:None)
    output=tmp_path/'attempt'
    monkeypatch.setattr(r,'ATTEMPT',output)
    monkeypatch.setattr(r,'verify',lambda:{'identity':'CPU'})
    monkeypatch.setattr(r,'selected',lambda:(_ for _ in ()).throw(FileNotFoundError('no fixed6 in CPU fixture')))
    result=r.execute(output)
    assert seen[0][0][:2]==[str(r.s.TRAIN),str(r.OLD/'od_train.py')]
    assert seen[0][1]=='MIG-CPU-qualification-exact-assignment'
    assert len(result['readout_inventory'])==24 and not any(x['recorded'] for x in result['readout_inventory'])
    stage=tmp_path/'collector';stage.mkdir()
    argv=r.collector_argv(stage,tmp_path/'rows',9999999999.)
    suite.command(stage,'CPU-collector',argv,10,9999999999.)
    assert seen[1][1]==''
    assert r.s.read(stage/'CPU-collector-COMMAND.json')['gpu_visible_to_command'] is False

def test_exact_cli_original_corpus_and_deadlines():
    module=r.collector()
    argv=r.collector_argv(Path('/tmp/service'),Path('/tmp/rows'),123.)
    parsed=module.parse_args(argv[2:])
    assert (parsed.mode,parsed.plan,parsed.start,parsed.stop)==('free','FREE_PLAN.json',0,24)
    assert parsed.output==Path('/tmp/rows')
    assert r.training_argv(Path('/tmp/new'),123.)[-4:]==['--output','/tmp/new/training','--deadline','123.0']
    assert r.train_deadline(100.,5320.)==3700.
    assert r.train_deadline(4000.,5320.)==3820.
    assert r.binding_module().selected.__globals__['RECOVERY_TRAINING']==r.ATTEMPT/'training'
    assert r.binding_module().s.ATTEMPT==r.s.ATTEMPT
    assert r.binding_module().s.ROOT==r.OLD
    assert len(r.inventory(Path('/tmp/new')))==24
    with pytest.raises(ValueError):r.check_output(Path('/tmp/wrong'))

def test_original_corpus_and_binding_failure_no_partial_substitution():
    episodes=r.s.corpus()
    assert len(episodes)==72
    assert len(r.s.read(r.OLD/'inputs/FREE_PLAN.json'))==24
    with pytest.raises(FileNotFoundError):r.selected()

def test_six_checkpoint_new_directory_and_original_corpus_ancestry(tmp_path,monkeypatch):
    module=r.binding_module();directory=tmp_path/'training';directory.mkdir()
    monkeypatch.setattr(module,'RECOVERY_TRAINING',directory)
    previous=None;identity=r.s.verify()['identity'];corpus=r.s.sha(r.s.ATTEMPT/'capture/CORPUS_READY.json')
    for step in range(1,7):
        path=directory/f'checkpoint-{step:04}';path.mkdir()
        # Authored byte fixtures test namespace/ancestry, not real optimizer contents.
        for name in ('adapter_model.safetensors','adapter_config.json','optimizer.pt','rng_state.pt'):r.s.write(path/name,dict(cpu_fixture=True,step=step))
        files={p.name:r.s.sha(p) for p in path.iterdir()}
        state=dict(step=step,epoch=step,cursor=0,identity=identity,corpus_sha256=corpus,previous_state_sha256=previous,files_sha256=files)
        r.s.write(path/'state.json',state);previous=r.s.sha(path/'state.json')
    chosen=dict(checkpoint=str(path),step=6,state_sha256=previous,adapter_sha256=files['adapter_model.safetensors'],config_sha256=files['adapter_config.json'])
    r.s.write(directory/'SELECTION.json',chosen)
    r.s.write(directory/'RESULT.json',dict(complete=True,identity=identity,optimizer_steps=6,selected=chosen,starting_adapter_sha256=r.s.starting_policy()['adapter_sha256'],fresh_optimizer=True,child_loaded=False,child_updated=False))
    assert module.selected('sft6')==chosen
    binding=module.binding('sft6')
    assert binding['models'][binding['role_map']['root']]['path']==str(path)
    assert binding['models'][binding['fixed_child']]['adapter_sha256']==r.s.CHILD_SHA
    state_path=path/'state.json';original_read=r.s.read
    monkeypatch.setattr(r.s,'read',lambda p:{**original_read(p),'corpus_sha256':'wrong'} if Path(p)==state_path else original_read(p))
    with pytest.raises(ValueError,match='ancestry'):module.selected('sft6')

def test_actual_collector_entry_exact_argv_and_runtime_alias(tmp_path,monkeypatch):
    import importlib.util
    import sys
    spec=importlib.util.spec_from_file_location('completion_entry_fixture',r.ROOT/'collect.py');entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
    output=tmp_path/'attempt';monkeypatch.setattr(r,'ATTEMPT',output);monkeypatch.setattr(r,'verify',lambda:{})
    actual=r.collector();seen=[]
    async def run(args):
        import od_binding
        import od_study
        assert od_binding is r.binding_module() and od_study is r.s
        seen.append(args)
    monkeypatch.setattr(actual,'run',run)
    argv=r.collector_argv(output/'service-sft6',output/'sft6/free',123.)
    monkeypatch.setattr(sys,'argv',argv[1:]);entry.main()
    assert len(seen)==1 and (seen[0].mode,seen[0].start,seen[0].stop)==('free',0,24)
    argv[argv.index('--mode')+1]='capture';monkeypatch.setattr(sys,'argv',argv[1:])
    with pytest.raises(ValueError,match='only original24'):entry.main()
