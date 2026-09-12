"""Bounded actual entrypoint and two-turn CPU regression; no native GPU process."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch
import owner
import service
import study as s


def entrypoints():
    directory=Path(tempfile.mkdtemp(prefix='cpu-service-entry-',dir=s.ROOT))
    receipts=[];suite=owner.dependencies();original_load=s.load
    def loader(name,path):
        module=original_load(name,path)
        if name=='controller_screen_accepted_launcher':
            module._port_free=lambda port:True
            module._wait_endpoint_model=lambda *args,**kwargs:None
        return module
    for arm in s.ARMS:
        stage=directory/arm;stage.mkdir();binding=s.binding(arm)
        s.write_x(stage/'BINDING.json',binding)
        calls=[]
        class NoGPUProcess:
            pid=999991
            def __init__(self,command,**kwargs):
                assert command==[str(s.NATIVE.with_name('inference')),'@',str(stage/'service/inference.json')]
                assert kwargs['env']['VLLM_BATCH_INVARIANT']=='0'
                assert str(service.environment_adapter().DRIVER_LIBRARY) in kwargs['env']['LD_LIBRARY_PATH']
                calls.append(command)
        argv=['service.py','--binding',str(stage/'BINDING.json'),'--run-dir',str(stage/'service')]
        with patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_FIXTURE_ONLY','STRICT_RLM_CALIBRATION_API_KEY':'CPU-fixture-only'}), \
             patch.object(sys,'argv',argv),patch.object(s,'load',loader),patch.object(service.subprocess,'Popen',NoGPUProcess):
            service.main()
        assert len(calls)==1 and s.read(stage/'service/SERVER_READY.json')['enable_lora'] is False
        s.write_x(stage/'SERVICE_REQUEST.json',{'command':[str(s.NATIVE),str(s.ROOT/'service.py'),'--binding',
            str(stage/'BINDING.json'),'--run-dir',str(stage/'service')],'gpu':'CPU_FIXTURE_ONLY'})
        with patch.object(suite.life,'observe',lambda pid:None):
            assert suite.life.claim_service(stage/'service') is None
        receipts.append({'arm':arm,'entrypoint':str(s.ROOT/'service.py'),'directory':str(stage),
            'actual_config_and_command_binding_passed':True,'GPU_launch_stubbed':True})
    return receipts


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (s.ROOT/'CPU_EVIDENCE_FINAL.json').exists()
    starts=time.time();services=entrypoints()
    argv=[str(s.NATIVE),'-m','pytest','-q','test_screen.py','--basetemp',str(s.ROOT/'cpu-fixture-004')]
    assert not (s.ROOT/'cpu-fixture-004').exists()
    result=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},
                          capture_output=True,text=True,timeout=300)
    evidence={'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
        'elapsed_seconds':time.time()-starts,'actual_service_entrypoint_cpu_checks':services,
        'GPU_calls':0,'model_weight_loads':0,'fake_native_responses':True,
        'actual_cached_CPU_container_and_Python_tool':True,'generated_fixture_code_is_operator_authored':True,
        'prior_preparation_fixtures_preserved':['cpu-fixture-001','cpu-fixture-002','cpu-fixture-003'],
        'fixture_files_sha256':{str(p):s.sha(p) for p in (s.ROOT/'cpu-fixture-004').rglob('*.json')},
        'fidelity_levels':['stop_removed_raw_tokens','native_message_content','harness_root_reply']}
    s.write_x(s.ROOT/'CPU_EVIDENCE_FINAL.json',evidence)
    print(result.stdout);print({'returncode':result.returncode,'elapsed_seconds':evidence['elapsed_seconds']})
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
