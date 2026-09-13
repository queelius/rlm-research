"""One current allocation-native service, genuine base plus sole fixed cp1 LoRA."""
import argparse
import json
import os
import signal
import time
import traceback
import collect
import metrics
import study as s

def execute(seconds):
    ready=s.verify()
    if seconds!=s.OWNER_SECONDS or s.ATTEMPT.exists():raise ValueError('exact cap and new attempt required')
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('MAIN-owned exclusive GPU and private credential required')
    started=time.time();end=started+seconds;s.ATTEMPT.mkdir(parents=True)
    directory=s.ATTEMPT/'service';directory.mkdir();binding=s.binding()
    s.write_x(s.ATTEMPT/'OWNER_START.json',dict(ready_sha256=s.sha(s.READY),ready_identity=ready['identity'],
        started_epoch=started,owner_seconds=seconds,science_seconds=s.SCIENCE_SECONDS,planned_calls=72))
    def interrupted(sig,frame):raise TimeoutError(f'owner interrupted {sig}')
    previous={sig:signal.signal(sig,interrupted) for sig in (signal.SIGALRM,signal.SIGINT,signal.SIGTERM)}
    signal.setitimer(signal.ITIMER_REAL,seconds-30)
    errors=[];phases={};suite=None;released=False;qualified=False
    try:
        suite=s.dependencies();suite.start_service(directory,binding,min(started+285,end-90))
        service=directory/'service';assert s.read(service/'BINDING.json')==binding
        config=s.read(service/'inference.json')['vllm'];descriptor=s.read(service/'endpoint-original.json')
        preflight=s.read(directory/'SUITE_PREFLIGHT.json');cards={x['id']:x for x in preflight['models']['data']}
        assert str(s.train.BASE) in cards and cards[str(s.train.BASE)]['root']==str(s.train.BASE)
        assert descriptor['base_model']['path']==str(s.train.BASE) and descriptor['model_alias']==s.train.ALIAS
        assert descriptor['adapter']['model_sha256']==binding['models'][s.train.ALIAS]['adapter_sha256']
        assert descriptor['adapter']['config_sha256']==binding['models'][s.train.ALIAS]['config_sha256']
        assert config['enable_lora'] is True and config['max_model_len']==8192
        start=s.read(service/'SERVER_START.json');assert start['launcher_sha256']==s.sha(s.RUNTIME/'service_wrapper_v2.py')
        runtime=dict(service_wrapper=str(suite.SERVE),service_wrapper_sha256=s.sha(suite.SERVE),
            preflight_sha256=s.sha(directory/'SUITE_PREFLIGHT.json'),server_start_sha256=s.sha(service/'SERVER_START.json'),
            endpoint_sha256=s.sha(service/'endpoint-original.json'),inference_config_sha256=s.sha(service/'inference.json'),
            vllm={k:config.get(k) for k in ('dtype','max_model_len','enable_lora','lora_dtype','max_loras','max_cpu_loras',
                'max_lora_rank','enable_prefix_caching','enforce_eager','max_num_seqs','enable_fp32_lm_head')},
            parent_batch_invariant_env=os.environ.get('VLLM_BATCH_INVARIANT'),actual_base_card=cards[str(s.train.BASE)],
            genuine_base_control=True,cp1_adapter_cast='auto BF16 serving from FP32 stored adapter',
            no_batch_invariance_or_old_runtime_pooling_claim=True,credentials_persisted=False)
        s.write_x(s.ATTEMPT/'RUNTIME.json',runtime);qualified=True
        phases['startup_seconds']=time.time()-started;science=time.time()
        endpoint=f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate"
        result=collect.execute(endpoint,s.ATTEMPT,min(science+s.SCIENCE_SECONDS,end-90))
        phases['science_seconds']=time.time()-science;errors.extend(result['errors'])
        s.write_x(s.ATTEMPT/'COLLECTION.json',result)
    except Exception as e:errors.append(dict(stage='owner',type=type(e).__name__,detail=str(e),traceback=traceback.format_exc()))
    finally:
        signal.setitimer(signal.ITIMER_REAL,60);cleanup=time.time()
        if suite is not None:
            try:
                suite.release_service(directory);stop=s.read(directory/'SERVICE_STOPPED.json')
                released=bool(stop['all_owned_process_identities_exited'] and stop['ports_free'])
            except Exception as e:errors.append(dict(stage='release',type=type(e).__name__,detail=str(e),traceback=traceback.format_exc()))
        else:released=True
        phases['cleanup_seconds']=time.time()-cleanup
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    result=metrics.summarize(s.ATTEMPT,qualified);result.update(phases=phases,errors=errors,released=released)
    s.write_x(s.ATTEMPT/'RESULT.json',result)
    terminal=dict(complete=bool(result['complete'] and not errors and released),runtime_qualified=qualified,released=released,
        errors=errors,elapsed_seconds=time.time()-started,result_sha256=s.sha(s.ATTEMPT/'RESULT.json'))
    s.write_x(s.ATTEMPT/'OWNER_TERMINAL.json',terminal);return terminal

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--outer-seconds',type=int,default=s.OWNER_SECONDS);a=p.parse_args()
    if a.command=='verify':print(s.verify()['identity'])
    else:
        terminal=execute(a.outer_seconds);print(json.dumps(terminal));raise SystemExit(0 if terminal['complete'] else 1)
