"""Current B05 eager native runtime with cached full-weight Qwen3-8B."""
import argparse,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
import study
DRIVER_LIB=Path('/export/software/system/nvidia/580.126.20/lib');DRIVER_BIN=Path('/export/software/system/nvidia/580.126.20/bin')
LAUNCH=Path('/project/alex_phd/runs/rlm-research-r4/sidecars/strict-rlm-temperature-adherence-v1/scripts/launch.py')
RUNTIME_SOURCE=study.SOURCE/'outputs/attempt-003/RUNTIME.json'
def main():
    p=argparse.ArgumentParser();p.add_argument('--binding',type=Path,required=True);p.add_argument('--run-dir',type=Path,required=True);a=p.parse_args()
    binding=study.read(a.binding);assert binding==study.binding() and binding['adapter'] is None
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','');assert gpu and ',' not in gpu and DRIVER_LIB.is_dir() and DRIVER_BIN.is_dir()
    spec=importlib.util.spec_from_file_location('b05_qwen8_launch',LAUNCH);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    if any(not helper._port_free(x) for x in (18601,18611,18621)):raise ValueError('owned ports occupied')
    a.run_dir.mkdir(parents=True,exist_ok=False);config=study.read(RUNTIME_SOURCE);key=os.environ['STRICT_RLM_CALIBRATION_API_KEY'];v=config['vllm']
    v.update(model=str(study.MODEL),served_model_name=[study.MODEL_ALIAS],api_key=[key],gpu_memory_utilization=.82,max_model_len=8192,max_num_seqs=4,enable_lora=False,enable_prefix_caching=False,enforce_eager=True,generation_config='vllm',reasoning_parser=None,tool_call_parser='hermes',worker_extension_cls='report_worker.ReportWorker')
    config['output_dir']=str(a.run_dir/'launcher')
    from prime_rl.configs.inference import InferenceConfig
    InferenceConfig.model_validate(config);study.write_x(a.run_dir/'inference.json',config);study.write_x(a.run_dir/'BINDING.json',binding)
    env=helper._server_environment(helper._environment(),0);libs=[x for x in env.get('LD_LIBRARY_PATH','').split(':') if x and '/export/software/system/nvidia/' not in x and 'nvidia-driver-' not in x]
    bins=[x for x in env.get('PATH','').split(':') if x and '/export/software/system/nvidia/' not in x]
    env.update(CUDA_VISIBLE_DEVICES=gpu,LD_LIBRARY_PATH=':'.join([str(DRIVER_LIB),*libs]),PATH=':'.join([str(DRIVER_BIN),*bins]),HF_HOME='/project/alex_phd/research-cache/huggingface-runtime',HF_HUB_OFFLINE='1',PYTHONDONTWRITEBYTECODE='1',VLLM_BATCH_INVARIANT='1',STRICT_RLM_CALIBRATION_API_KEY=key,REPORT_DISPATCH_RECEIPT=str(a.run_dir/'ACTUAL_DISPATCH.json'))
    env['PYTHONPATH']=str(study.MUSIQUE)+((':'+env['PYTHONPATH']) if env.get('PYTHONPATH') else '')
    command=[sys.executable,str(study.MUSIQUE/'engine_entry_v2.py'),'@',str(a.run_dir/'inference.json')]
    with (a.run_dir/'inference.log').open('x') as log:process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    study.write_x(a.run_dir/'SERVER_START.json',{'pid':process.pid,'gpu':gpu,'started':time.time(),'command':command,'launcher_sha256':study.sha(Path(__file__))})
    model=binding['checkpoint'];endpoint={'host':'127.0.0.1','port':18601,'replica':0,'api_key_env':'STRICT_RLM_CALIBRATION_API_KEY','model_alias':study.MODEL_ALIAS,'base_model':model,'adapter':None,'inference_only':True,'prime_inference_config':str(a.run_dir/'inference.json'),'vllm_version':'0.28.0','max_model_len':8192}
    helper._wait_endpoint_model(endpoint,process,study.MODEL_ALIAS,timeout=285);endpoint['gpu']=gpu;study.write_x(a.run_dir/'endpoint-original.json',endpoint);study.write_x(a.run_dir/'SERVER_READY.json',{'pid':process.pid,'ready':time.time(),'model':model,'enable_lora':False})
if __name__=='__main__':main()
