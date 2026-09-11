import prepare
import study as s
def main():
 b=prepare.build(False);expected={"PLAN.json":b["plan"],"REQUESTS.json":b["requests"],"PUBLIC.json":b["public"],"HOST_GOLD.json":b["host"]}
 for n,x in expected.items():
  if s.read(s.ROOT/"inputs"/n)!=x:raise ValueError("input drift "+n)
 old=s.read(s.CEILING/"inputs/PLAN.json");assert len(old)==len(b["plan"])==40
 assert [(x["context_id"],x["record_ids"],x["seed"]) for x in b["plan"]]==[(x["context_id"],x["ids"],x["seed"]) for x in old]
 if s.ATTEMPT.exists():raise ValueError("attempt exists")
 analysis=s.SIDE.parent/"analyses/root-j1-sufficient-statistics-live-2026-09-10";idea=s.SIDE.parent/"ideas"
 sources=[s.ROOT/n for n in ("DESIGN.md","PLAN.md","study.py","protocol.py","prepare.py","collect.py","owner.py","seal.py","test_contract.py")]+[s.V1/"READY.json",s.V1/"READY_WITHDRAWAL.json",s.V1/"study.py",s.V1/"protocol.py",s.V1/"prepare.py",s.V1/"owner.py",idea/"2026-09-10-change-information-selective-repair-revision-v2.yaml",idea/"2026-09-10-change-information-selective-repair-ERRATUM.md",idea/"2026-09-10-change-information-selective-repair-ERRATUM-2.md",analysis/"METHOD.md",s.CEILING/"READY.json",s.CEILING/"inputs/PLAN.json",s.CEILING/"outputs/attempt-001/OWNER_TERMINAL.json",s.SIDE/"leaf-adapter-by-granularity-v1/bg_collect.py",s.SIDE/"runtime-an27-5780-v1/service_wrapper_v2.py",prepare.TOKENIZER]
 inputs=sorted((s.ROOT/"inputs").glob("*.json"))+[s.ROOT/"CPU_INPUT_NATIVE.json"]
 ready={"schema":"root-j1-sufficient-statistics-ready-v2","status":"READY_CPU_ONLY_MAIN_LAUNCH_REQUIRED","recovery_of_withdrawn_v1":True,"planned_calls":40,"planned_episodes":8,"mapping":{"size64":{"episodes":4,"chunks_each":2,"records_per_chunk":32},"size256":{"episodes":4,"chunks_each":8,"records_per_chunk":32}},"shared_historical_control_calls":40,"control_calls_reexecuted":0,"same_scientific_requests_as_v1":True,"one_a100":True,"outer_seconds":1200,"workers":4,"request_cap_seconds":90,"root_model_calls":0,"no_training":True,"no_retry":True,"runtime_fallback":False,"gold_in_prompt":False,"source_sha256":{str(p):s.sha(p) for p in sources},"input_sha256":{str(p):s.sha(p) for p in inputs}};ready["identity"]=s.digest(ready);s.write(s.ROOT/"READY.json",ready);print(ready["identity"])
if __name__=="__main__":main()
