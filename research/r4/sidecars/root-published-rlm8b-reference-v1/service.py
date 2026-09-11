"""Full-weight8B configuration on the proven Prime/an27 launcher seam."""
import argparse,os,subprocess,time
from pathlib import Path
import rv_study as s
OLD=s.SIDE/'strict-rlm-temperature-adherence-v1'
def helper():return s.load('rv8b_qualified_launcher',OLD/'scripts/launch.py','d511492f9add5a8bcd7325b7899bf844febe95512aa7c562f0666c9191d6609a')
def config(model,directory,key):
    value=s.read(OLD/'configs/inference-replica0.json');v=value['vllm']
    v.update(model=model['path'],served_model_name=[model['alias']],dtype='bfloat16',enable_lora=False,enforce_eager=True,enable_prefix_caching=False,generation_config='vllm',max_model_len=32768,max_num_seqs=2,max_num_batched_tokens=4096,gpu_memory_utilization=.85,api_key=[key],reasoning_parser=None,tool_call_parser=None,chat_template=str(s.TEMPLATE))
    for k in ('max_loras','max_lora_rank','max_cpu_loras','lora_dtype'):v.pop(k,None)
    value.update(enable_fp32_lm_head=False,enable_fp32_router_logits=False,output_dir=str(directory/'launcher'));return value
def descriptor(model,directory):return dict(host='127.0.0.1',port=18601,replica=0,api_key_env='STRICT_RLM_CALIBRATION_API_KEY',model_alias=model['alias'],base_model=model,adapter=None,inference_only=True,prime_inference_config=str(directory/'inference.json'),vllm_version='0.28.0',max_model_len=32768,chat_template_sha256=s.sha(s.TEMPLATE))
def launch(binding_path,directory):
    from prime_rl.configs.inference import InferenceConfig
    binding=s.read(binding_path);policy=binding['policy'];model=s.MODELS[policy]
    if binding['checkpoint']!=model or binding['model_manifest_sha256']!=s.sha(Path(model['path'])/'local-research-manifest.json'):raise ValueError('full-weight binding changed')
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('one MAIN-assigned GPU required')
    h=helper()
    if any(not h._port_free(p) for p in (18601,18611,18621)):raise ValueError('owned service ports occupied')
    directory.mkdir(parents=True,exist_ok=False);env=h._server_environment(h._environment(),0);env['CUDA_VISIBLE_DEVICES']=gpu
    libs=[p for p in env.get('LD_LIBRARY_PATH','').split(':') if p and '580.126.09' not in p and p!='/export/software/system/nvidia/580.159.04/lib']
    env['LD_LIBRARY_PATH']=':'.join(['/export/software/system/nvidia/580.159.04/lib',*libs]);env['PATH']=env['PATH'].replace('/export/software/system/nvidia/580.126.09/bin','/export/software/system/nvidia/580.159.04/bin')
    env.update(HF_HUB_OFFLINE='1',PYTHONDONTWRITEBYTECODE='1',HF_HOME='/project/alex_phd/research-cache/huggingface-runtime')
    key=os.environ['STRICT_RLM_CALIBRATION_API_KEY'];value=config(model,directory,key);InferenceConfig.model_validate(value)
    s.write(directory/'inference.json',value);s.write(directory/'BINDING.json',binding)
    command=[str(h.PRIME_ENV/'bin/inference'),'@',str(directory/'inference.json')]
    with (directory/'inference.log').open('x') as log:process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    s.write(directory/'SERVER_START.json',dict(pid=process.pid,gpu=gpu,started=time.time(),command=command,launcher_sha256=s.sha(__file__)))
    endpoint=descriptor(model,directory);endpoint['gpu']=gpu
    try:
        h._wait_endpoint_model(endpoint,process,model['alias'],timeout=145);s.write(directory/'endpoint-original.json',endpoint);s.write(directory/'SERVER_READY.json',dict(pid=process.pid,ready=time.time(),model=model,enable_lora=False))
    except BaseException as e:s.write(directory/'SERVER_FAILURE.json',dict(error_type=type(e).__name__,error=str(e)));raise
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--binding',type=Path,required=True);ap.add_argument('--run-dir',type=Path,required=True);a=ap.parse_args();launch(a.binding,a.run_dir)
