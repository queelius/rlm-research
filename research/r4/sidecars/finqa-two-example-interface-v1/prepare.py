"""Freeze existing16 with synthetic demonstrations, actual CPU fixture, seal."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import interface
import owner
import study


def main():
    assert not study.READY_RUN.exists()
    assert study.sha(study.BASE_READY)==study.BASE_READY_SHA
    original=study.read(study.parent.INPUTS)
    plan={**original,"schema":"finqa-fixed16-two-example-native-plan-v1","prompts":{},
          "intervention":"two synthetic demonstrations, same facts/questions and arm-specific response representation",
          "synthetic_facts_questions":interface.FACTS}
    audits=[]
    for call in plan["calls"]:
        key=study.call_id(call);public=plan["contexts"][call["context_index"]]["public"]
        prompt=interface.prompt(public,call["kind"]);request=study.request_body(prompt,call["seed"],call["max_tokens"])
        assert request["sampling_params"]["max_tokens"]==384
        plan["prompts"][key]=prompt
        audits.append({"call_id":key,"example_id":call["example_id"],"arm":call["kind"],"seed":call["seed"],
                       "input_tokens":len(request["token_ids"]),"prefix_token_ids_sha256":study.digest(request["token_ids"]),
                       "shared_public_sha256":study.digest(public),"request":request})
    study.write_x(study.INPUTS,plan)
    study.write_x(study.HOST,study.read(study.parent.HOST))
    study.write_x(study.ROOT/"TOKEN_AUDIT.json",{"schema":"finqa-two-example-native32-token-audit-v1","calls":audits})
    command=[str(study.NATIVE),"-m","pytest","-q","test_interface.py","--basetemp=cpu-fixture-seal-001"]
    tested=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True)
    study.write_x(study.ROOT/"CPU_TESTS.json",{"command":command,"returncode":tested.returncode,"stdout":tested.stdout,"stderr":tested.stderr,
                                            "actual_frozen_pair_HTTP":True,"model_calls":0,"GPU_calls":0})
    assert tested.returncode==0,tested.stdout
    owner.implementation()
    base_ready=study.read(study.BASE_READY);closure=dict(base_ready["closure_sha256"])
    analysis=study.ROOT.parents[1]/"analyses/finqa-scalar-vs-dsl-independent-2026-09-12"
    paths=list(study.ROOT.glob("*.py"))+[study.ROOT/"RUNBOOK.md",study.INPUTS,study.HOST,study.ROOT/"TOKEN_AUDIT.json",study.ROOT/"CPU_TESTS.json",
            study.BASE_READY,study.PARENT/"outputs/attempt-001/RESULT.json",study.PARENT/"outputs/attempt-001/OWNER_TERMINAL.json",
            analysis/"outcome-002/REPORT.json",analysis/"MECHANISM_REVIEW.json",analysis/"FINDINGS.md"]
    for path in paths:closure[str(path)]=study.sha(path)
    # Pin the actual native fixture, not only its text success report.
    for path in (study.ROOT/"cpu-fixture-seal-001").rglob("*.json"):closure[str(path)]=study.sha(path)
    ready={k:v for k,v in base_ready.items() if k not in ("identity","closure_sha256","created_utc","argv","schema")}
    ready.update({"schema":"finqa-two-example-interface-ready-v1","created_utc":datetime.now(timezone.utc).isoformat(),
                  "argv":[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--outer-seconds","700"],
                  "condition":"two synthetic demonstrations, same questions/facts and requested representation per arm",
                  "baseline_ready_sha256":study.BASE_READY_SHA,"baseline_result_sha256":study.BASE_RESULT_SHA,
                  "all_eval_evidence_and_call_seeds_identical":True,"interpreter_and_output_caps_unchanged":True,
                  "adaptive_exposed_panel_not_method_claim":True,"two_examples_not_SFT_or_RL":True,
                  "model_input_token_max":max(r["input_tokens"] for r in audits),"input_cap":8192,
                  "closure_sha256":dict(sorted(closure.items()))})
    ready["identity"]=study.digest(ready);study.write_x(study.READY_RUN,ready);study.verify()
    print(json.dumps({"path":str(study.READY_RUN),"sha256":study.sha(study.READY_RUN),"identity":ready["identity"],
                      "max_input_tokens":ready["model_input_token_max"],"closure_files":len(closure)}))


if __name__=="__main__":main()
