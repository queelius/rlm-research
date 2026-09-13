"""One qualified dual-LoRA service; 72 frozen held calls across base/local/joint."""
import argparse,json,os,signal,time,traceback
import collect,metrics,study as s
def execute(seconds):
    ready=s.verify()
    if seconds!=s.OWNER_SECONDS or s.ATTEMPT.exists():raise ValueError("exact cap and new attempt required")
    gpu=os.environ.get("CUDA_VISIBLE_DEVICES","")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):raise ValueError("MAIN-owned exclusive GPU and credential required")
    started=time.time();end=started+seconds;s.ATTEMPT.mkdir(parents=True);directory=s.ATTEMPT/"service";directory.mkdir();binding=s.binding()
    s.write_x(s.ATTEMPT/"OWNER_START.json",{"ready_sha256":s.sha(s.READY),"ready_identity":ready["identity"],"started_epoch":started,"owner_seconds":seconds,"science_seconds":s.SCIENCE_SECONDS,"planned_calls":72})
    def interrupted(sig,_frame):raise TimeoutError(f"owner interrupted {sig}")
    previous={sig:signal.signal(sig,interrupted) for sig in (signal.SIGALRM,signal.SIGINT,signal.SIGTERM)};signal.setitimer(signal.ITIMER_REAL,seconds-30)
    errors=[];phases={};suite=None;released=False;qualified=False
    try:
        suite=s.dependencies();suite.start_service(directory,binding,min(started+285,end-90));service=directory/"service"
        assert s.read(service/"BINDING.json")==binding;config=s.read(service/"inference.json")["vllm"];descriptor=s.read(service/"endpoint-original.json")
        preflight=s.read(directory/"SUITE_PREFLIGHT.json");cards={row["id"]:row for row in preflight["models"]["data"]}
        assert descriptor["base_model"]["path"]==str(s.BASE)
        for alias,model in binding["models"].items():assert cards[alias]["root"]==model["path"] and cards[alias]["parent"]==str(s.BASE)
        assert config["enable_lora"] is True and config["max_model_len"]==8192 and config["max_loras"]>=2
        start=s.read(service/"SERVER_START.json");assert start["launcher_sha256"]==s.sha(s.ROOT.parent/"runtime-an22-5801-v1/service_wrapper_v2.py")
        s.write_x(s.ATTEMPT/"RUNTIME.json",{"service_wrapper":str(suite.SERVE),"service_wrapper_sha256":s.sha(suite.SERVE),
          "preflight_sha256":s.sha(directory/"SUITE_PREFLIGHT.json"),"server_start_sha256":s.sha(service/"SERVER_START.json"),
          "endpoint_sha256":s.sha(service/"endpoint-original.json"),"inference_config_sha256":s.sha(service/"inference.json"),
          "actual_model_cards":cards,"base_control_no_adapter":True,"two_fixed_step1_adapters":True,"credentials_persisted":False})
        qualified=True;phases["startup_seconds"]=time.time()-started;science=time.time();endpoint=f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate"
        collection=collect.execute(endpoint,s.ATTEMPT,min(science+s.SCIENCE_SECONDS,end-90));phases["science_seconds"]=time.time()-science;errors.extend(collection["errors"]);s.write_x(s.ATTEMPT/"COLLECTION.json",collection)
    except Exception as error:errors.append({"stage":"owner","type":type(error).__name__,"detail":str(error),"traceback":traceback.format_exc()})
    finally:
        signal.setitimer(signal.ITIMER_REAL,60);cleanup=time.time()
        if suite is not None:
            try:suite.release_service(directory);stop=s.read(directory/"SERVICE_STOPPED.json");released=bool(stop["all_owned_process_identities_exited"] and stop["ports_free"])
            except Exception as error:errors.append({"stage":"release","type":type(error).__name__,"detail":str(error),"traceback":traceback.format_exc()})
        else:released=True
        phases["cleanup_seconds"]=time.time()-cleanup;signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    result=metrics.summarize(s.ATTEMPT,qualified);result.update(phases=phases,errors=errors,released=released);s.write_x(s.ATTEMPT/"RESULT.json",result)
    terminal={"complete":bool(result["complete"] and not errors and released),"runtime_qualified":qualified,"released":released,"errors":errors,"elapsed_seconds":time.time()-started,"result_sha256":s.sha(s.ATTEMPT/"RESULT.json")};s.write_x(s.ATTEMPT/"OWNER_TERMINAL.json",terminal);return terminal
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("command",choices=("verify","run"));p.add_argument("--outer-seconds",type=int,default=700);a=p.parse_args()
 if a.command=="verify":print(s.verify()["identity"])
 else:
  value=execute(a.outer_seconds);print(json.dumps(value));raise SystemExit(0 if value["complete"] else 1)
