import prepare
import study as s
def main():
 b=prepare.build(write=False);expected={"PLAN.json":b["plan"],"REQUESTS.json":b["requests"],"PUBLIC.json":b["public"],"HOST_GOLD.json":b["host"]}
 for n,x in expected.items():
  if s.read(s.ROOT/"inputs"/n)!=x:raise ValueError("input drift "+n)
 old=s.read(s.CEILING/"inputs/PLAN.json");assert len(b["plan"])==len(old)==40
 assert [(x["context_id"],x["record_ids"],x["seed"]) for x in b["plan"]]==[(x["context_id"],x["ids"],x["seed"]) for x in old]
 if s.ATTEMPT.exists():raise ValueError("attempt exists")
 idea=s.SIDE.parent/"ideas";analysis=s.SIDE.parent/"analyses/root-j1-sufficient-statistics-live-2026-09-10"
 sources=[s.ROOT/n for n in ("DESIGN.md","PLAN.md","study.py","protocol.py","prepare.py","collect.py","owner.py","seal.py","test_contract.py")]+[idea/"2026-09-10-change-information-selective-repair.yaml",idea/"2026-09-10-change-information-selective-repair.md",idea/"2026-09-10-change-information-selective-repair-revision-v2.yaml",idea/"2026-09-10-change-information-selective-repair-ERRATUM.md",analysis/"METHOD.md",s.CEILING/"READY.json",s.CEILING/"inputs/PLAN.json",s.CEILING/"inputs/REQUESTS.json",s.CEILING/"outputs/attempt-001/OWNER_TERMINAL.json",s.SIDE/"leaf-adapter-by-granularity-v1/bg_collect.py",s.SIDE/"runtime-an27-5780-v1/service_wrapper_v2.py",prepare.TOKENIZER]
 inputs=sorted((s.ROOT/"inputs").glob("*.json"))+[s.ROOT/"CPU_INPUT_NATIVE.json"]
 ready={"schema":"root-j1-sufficient-statistics-ready-v1","status":"READY_CPU_ONLY_MAIN_LAUNCH_REQUIRED","planned_calls":40,"planned_episodes":8,"control_calls_reexecuted":0,"shared_historical_control_calls":40,"same_ceiling_chunks_seeds_record_order":True,"intentional_seed_reuse_for_paired_interface_comparison":True,"one_a100":True,"outer_seconds":1200,"workers":4,"request_cap_seconds":90,"root_model_calls":0,"no_training":True,"no_retry":True,"runtime_fallback":False,"gold_in_prompt":False,"bundle":["task_aware_prompt","statistics_format","LLM_summation"],"source_sha256":{str(p):s.sha(p) for p in sources},"input_sha256":{str(p):s.sha(p) for p in inputs}};ready["identity"]=s.digest(ready);s.write(s.ROOT/"READY.json",ready);print(ready["identity"])
if __name__=="__main__":main()
