import json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import checkpoint_repair as checkpoint
import study_repair as study
EXPECTED=study.SIDE/'runtime-an22-5801-v1/service_wrapper_v2.py'
def test_actual_start_service_argv_for_both_bindings(tmp_path,monkeypatch):
    bindings={arm:checkpoint.binding(arm) for arm in ('cp32','lr1e4')};suite=study.dependencies();seen=[]
    class Process:
        pid=424242;returncode=0
        def __init__(self,command,**kwargs):
            seen.append(command);service=Path(command[command.index('--run-dir')+1]);service.mkdir(parents=True);(service/'SERVER_READY.json').write_text('{}')
        def poll(self):return 0
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','cpu-fixture');monkeypatch.setattr(suite.life.v1,'ports_free',lambda:True)
    monkeypatch.setattr(suite.subprocess,'Popen',Process);monkeypatch.setattr(suite.life,'observe',lambda pid:{'pid':pid,'pgid':pid,'uid':os.getuid(),'start_ticks':1,'cmdline':[]})
    monkeypatch.setattr(suite.life,'safe_observation',lambda v:v);monkeypatch.setattr(suite,'observe_service',lambda d:None);monkeypatch.setattr(suite,'preflight',lambda s,b:None)
    for arm,binding in bindings.items():
        d=tmp_path/arm;d.mkdir();suite.start_service(d,binding,time.time()+10)
        request=json.loads((d/'SERVICE_REQUEST.json').read_text());assert Path(request['command'][1])==EXPECTED;assert json.loads((d/'BINDING.json').read_text())==binding
    assert len(seen)==2 and all(Path(x[1])==EXPECTED for x in seen)
