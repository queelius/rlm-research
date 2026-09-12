"""Previously served released-model configuration and qualified current-driver launcher."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
import study as s

ENV_SOURCE=s.SIDE/'helper-unseen-generalization-base4b-v1/service_wrapper_v2.py'
ENV_SHA='37617a6ae5f77023c79448738e4509b2c127ddf95e00435dd4cb87122b97bffd'


def environment_adapter():
    assert s.sha(ENV_SOURCE)==ENV_SHA
    with s.aliases({},ENV_SOURCE.parent):return s.load('controller_current_driver_environment',ENV_SOURCE)


def config(arm,directory,key):
    assert s.MODELS==s.qwen_source().MODELS
    return s.qwen_service().config(s.MODELS[arm],directory,key)


def main():
    from prime_rl.configs.inference import InferenceConfig
    parser=argparse.ArgumentParser();parser.add_argument('--binding',type=Path,required=True)
    parser.add_argument('--run-dir',type=Path,required=True);args=parser.parse_args()
    binding=s.read(args.binding);arm=binding['arm'];assert binding==s.binding(arm)
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN exclusive GPU required')
    adapter=environment_adapter();assert adapter.DRIVER_LIBRARY.is_dir() and adapter.DRIVER_BINARY.is_dir()
    launcher=s.qwen_service().OLD/'scripts/launch.py'
    assert s.sha(launcher)=='d511492f9add5a8bcd7325b7899bf844febe95512aa7c562f0666c9191d6609a'
    helper=s.load('controller_screen_accepted_launcher',launcher)
    assert all(helper._port_free(p) for p in (18601,18611,18621))
    args.run_dir.mkdir(parents=True,exist_ok=False)
    environment=adapter.adapt_environment(helper._server_environment(helper._environment(),0))
    environment.update(CUDA_VISIBLE_DEVICES=gpu,HF_HOME='/project/alex_phd/research-cache/huggingface-runtime',
        HF_HUB_OFFLINE='1',PYTHONDONTWRITEBYTECODE='1',VLLM_BATCH_INVARIANT='0')
    key=os.environ['STRICT_RLM_CALIBRATION_API_KEY'];environment['STRICT_RLM_CALIBRATION_API_KEY']=key
    value=config(arm,args.run_dir,key);InferenceConfig.model_validate(value)
    s.write_x(args.run_dir/'inference.json',value);(args.run_dir/'inference.json').chmod(0o600)
    s.write_x(args.run_dir/'BINDING.json',binding)
    s.write_x(args.run_dir/'ENVIRONMENT.json',{'GPU':gpu,'driver_library':str(adapter.DRIVER_LIBRARY),
        'VLLM_BATCH_INVARIANT':'0','HF_HUB_OFFLINE':'1','credentials_persisted':False})
    command=[str(s.NATIVE.with_name('inference')),'@',str(args.run_dir/'inference.json')]
    with (args.run_dir/'inference.log').open('x') as log:
        process=subprocess.Popen(command,env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    s.write_x(args.run_dir/'SERVER_START.json',{'pid':process.pid,'gpu':gpu,'started':time.time(),
        'command':command,'launcher_sha256':s.sha(__file__)})
    endpoint=s.qwen_service().descriptor(s.MODELS[arm],args.run_dir);endpoint['gpu']=gpu
    try:
        helper._wait_endpoint_model(endpoint,process,s.MODELS[arm]['alias'],timeout=285)
        s.write_x(args.run_dir/'endpoint-original.json',endpoint)
        s.write_x(args.run_dir/'SERVER_READY.json',{'pid':process.pid,'ready_epoch':time.time(),
            'model':s.MODELS[arm],'enable_lora':False})
    except BaseException as error:
        s.write_x(args.run_dir/'SERVER_FAILURE.json',{'type':type(error).__name__,'message':str(error)})
        raise


if __name__=='__main__':main()
