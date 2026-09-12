"""Post-seal runtime-boundary proof; V2 source and sealed test remain immutable."""
from __future__ import annotations
import importlib.util,json,os
from pathlib import Path
import time
ROOT=Path(__file__).resolve().parent
RUNTIME=ROOT.parent/'runtime-an22-5801-v1/service_wrapper_v2.py'
def load(name):
    s=importlib.util.spec_from_file_location('long_v2_runtime_'+name,ROOT/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test_actual_start_service_argv_for_both_real_bindings(tmp_path,monkeypatch):
    study=load('study_v2');checkpoint=load('checkpoint_v2')
    # Authenticate both bindings before stubbing the launcher's subprocess module (which is shared
    # with Python/torch internals).
    bindings={arm:checkpoint.binding(arm) for arm in ('base','checkpoint32')}
    suite=study.dependencies();observed=[]
    class Process:
        pid=424242;returncode=0
        def __init__(self,command,**kwargs):
            observed.append(command);service=Path(command[command.index('--run-dir')+1]);service.mkdir(parents=True);(service/'SERVER_READY.json').write_text('{}')
        def poll(self):return 0
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','cpu-fixture');monkeypatch.setattr(suite.life.v1,'ports_free',lambda:True)
    monkeypatch.setattr(suite.subprocess,'Popen',Process);monkeypatch.setattr(suite.life,'observe',lambda pid:{'pid':pid,'pgid':pid,'uid':os.getuid(),'start_ticks':1,'cmdline':[]});monkeypatch.setattr(suite.life,'safe_observation',lambda v:v);monkeypatch.setattr(suite,'observe_service',lambda d:None);monkeypatch.setattr(suite,'preflight',lambda s,b:None)
    for arm,binding in bindings.items():
        d=tmp_path/arm;d.mkdir();suite.start_service(d,binding,time.time()+10)
        request=json.loads((d/'SERVICE_REQUEST.json').read_text());assert Path(request['command'][1])==RUNTIME;assert json.loads((d/'BINDING.json').read_text())==binding
    assert len(observed)==2 and all(Path(row[1])==RUNTIME for row in observed)
