"""Exercise actual config/descriptor and real launch Popen seam, no GPU."""
import json,os,time,signal
from pathlib import Path
import pytest
import rv_study as s
import service as service_module
import owner
def test_actual_service_config_and_gpu_Popen(tmp_path,monkeypatch):
    seen=[]
    class Child:pid=12345
    def popen(argv,**kwargs):
        config=s.read(Path(argv[-1]));seen.append((argv,kwargs,config));return Child()
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','MIG-cpu-fixture-only');monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','synthetic-fixture-not-real')
    monkeypatch.setattr(service_module.subprocess,'Popen',popen)
    helper=service_module.helper();monkeypatch.setattr(helper,'_port_free',lambda p:True);monkeypatch.setattr(helper,'_wait_endpoint_model',lambda *a,**k:None)
    monkeypatch.setattr(service_module,'helper',lambda:helper)
    for policy in ('base','rlm'):
        binding=owner.binding(policy);root=tmp_path/policy;root.mkdir();s.write(root/'BINDING.json',binding)
        service_module.launch(root/'BINDING.json',root/'service')
        endpoint=s.read(root/'service/endpoint-original.json');assert endpoint['base_model']==s.MODELS[policy] and endpoint['max_model_len']==32768
        argv,kwargs,value=seen[-1];v=value['vllm']
        assert kwargs['env']['CUDA_VISIBLE_DEVICES']=='MIG-cpu-fixture-only'
        assert v['model']==s.MODELS[policy]['path'] and v['chat_template']==str(s.TEMPLATE)
        assert v['enable_lora'] is False and v['tool_call_parser'] is None and v['reasoning_parser'] is None
        assert v['max_model_len']==32768 and v['max_num_seqs']==2
        assert s.read(root/'service/SERVER_START.json')['launcher_sha256']==s.sha(s.ROOT/'service.py')
def test_owner_exact_collector_namespace_and_reserve():
    argv=owner.collector_argv('rlm',100)
    assert owner.validate_argv(argv)['policy']=='rlm'
    with pytest.raises(ValueError):owner.validate_argv([*argv[:-3],str(s.ATTEMPT/'base/rollout'),*argv[-2:]])
    assert owner.phase_deadline(0,0,3330,'base')==1620
    assert owner.phase_deadline(0,1000,3330,'rlm')==2620

def test_actual_owner_suite_to_service_config_and_cpu_collector(tmp_path,monkeypatch):
    runner=owner.suite();seen=[];processes={}
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','MIG-composed-fixture')
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','synthetic-fixture-not-real')
    helper=service_module.helper();monkeypatch.setattr(helper,'_port_free',lambda p:True);monkeypatch.setattr(helper,'_wait_endpoint_model',lambda *a,**k:None)
    monkeypatch.setattr(service_module,'helper',lambda:helper)
    class Child:
        returncode=0
        def __init__(self,pid):self.pid=pid
        def poll(self):return self.returncode
    def popen(argv,**kwargs):
        pid=40000+len(seen);seen.append((argv,kwargs))
        processes[pid]=dict(pid=pid,uid=os.getuid(),pgid=pid,start_ticks=1234,started_epoch=time.time(),argv=argv)
        if len(argv)>1 and argv[1]==str(s.ROOT/'service.py'):
            service_module.launch(Path(argv[3]),Path(argv[5]))
        return Child(pid)
    monkeypatch.setattr(runner.subprocess,'Popen',popen)
    monkeypatch.setattr(runner.life,'observe',lambda pid:processes.get(pid))
    monkeypatch.setattr(runner.life,'snapshot_descendants',lambda *a:None)
    monkeypatch.setattr(runner.life.v1,'ports_free',lambda:True)
    monkeypatch.setattr(runner,'preflight',lambda directory,binding:None)
    directory=tmp_path/'phase';directory.mkdir();runner.start_service(directory,owner.binding('base'),time.time()+30)
    actual=s.read(directory/'SERVICE_OWNER_V2.json')
    assert actual['command']==seen[1][0]
    assert seen[0][1]['env']['CUDA_VISIBLE_DEVICES']==seen[1][1]['env']['CUDA_VISIBLE_DEVICES']=='MIG-composed-fixture'
    assert s.read(directory/'service/inference.json')['vllm']['model']==s.MODELS['base']['path']
    runner.command(directory,'collector',owner.collector_argv('base',time.time()+10),10,time.time()+10)
    assert seen[-1][1]['env']['CUDA_VISIBLE_DEVICES']==''
    runner.LAUNCHERS.pop(directory)

def test_interrupted_phase_harvests_completed_coordinate(tmp_path):
    import rv_protocol as p
    row=p.plan()[0];value=dict(coordinate=row,score=dict(available=True,correct=True,format=True),calls=[dict(physical_attempt=True)])
    s.write(tmp_path/'base/rollout/episodes'/row['id']/'RESULT.json',value)
    result=owner.harvest(tmp_path,'base')
    assert len(result)==24 and result[0]==value
    assert sum(r['score']['available'] for r in result)==1

def test_interrupted_collector_reclaims_only_recorded_unreleased_container(tmp_path,monkeypatch):
    import types
    root=tmp_path/'rollout/episodes';names=['rv8b-'+'a'*32,'rv8b-'+'b'*32]
    for index,name in enumerate(names):s.write(root/str(index)/'worker/CONTAINER_COMMAND.json',dict(name=name))
    s.write(root/'0/worker/CONTAINER_STOPPED.json',dict(returncode=0))
    seen=[]
    monkeypatch.setattr(owner.subprocess,'run',lambda argv,**kw:(seen.append(argv) or types.SimpleNamespace(returncode=0,stdout='',stderr='')))
    assert owner.release_containers(tmp_path)
    assert seen==[[str(s.RUNTIME/'bin/docker'),'rm','--force','--ignore',names[1]]]

@pytest.mark.parametrize('cancel',[False,True])
def test_cancellation_stops_next_policy_ordinary_failure_does_not(tmp_path,monkeypatch,cancel):
    import types
    path=tmp_path/'attempt';monkeypatch.setattr(s,'ATTEMPT',path);monkeypatch.setattr(s,'verify',lambda:dict(identity='fixture'))
    monkeypatch.setattr(s,'load',lambda *a:types.SimpleNamespace(require_provider_credential=lambda:dict(passed=True)))
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','MIG-fixture')
    started=[];released=[]
    class Runner:
        def start_service(self,directory,binding,deadline):
            started.append(binding['policy'])
            if len(started)==1:
                if cancel:signal.getsignal(signal.SIGTERM)(signal.SIGTERM,None)
                raise RuntimeError('ordinary first phase failure')
        def command(self,*a):pass
        def release_service(self,directory):released.append(directory.name)
    monkeypatch.setattr(owner,'suite',lambda:Runner())
    result=owner.execute(path)
    assert started==(['base'] if cancel else ['base','rlm'])
    assert released==started
    assert len(s.read(path/'ROWS.json'))==48
