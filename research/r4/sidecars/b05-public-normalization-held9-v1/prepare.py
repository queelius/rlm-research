"""Freeze held9 raw/normalized36 calls before reading host labels; CPU only."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import normalize
import owner
import study


def main():
    assert not study.READY_RUN.exists()
    assert study.sha(study.TRAIN/"READY.json")==study.DATA_SHA
    held=study.read(study.TRAIN/"HELD_PUBLIC.json")["roots"]
    evaluations=[r for r in study.read(study.TRAIN/"EVAL_TASKS.json")["tasks"] if r["split"]=="held"]
    assert len(held)==9 and len(evaluations)==18
    tasks=[];calls=[];prompts={};requests={};audit=[]
    for index,root in enumerate(held):
        raw=root["prompt"];view,suffix=normalize.public_view(raw);normal=normalize.normalized_view(view);normalized=normalize.render(raw)
        assert view["stage"]==root["safe_root"]["stages"][root["selected_stage"]]
        ids=[r["implementation_id"] for r in view["stage"]["tables"]["implementations"]]
        assert set(ids)==set(root["known_ids"]) and len(ids)==len(set(ids))==root["width"]
        assert [r["implementation_id"] for r in normal["stage"]["effective_candidates"]]==ids
        tasks.append({"root_id":root["root_id"],"width":root["width"],"selected_stage":root["selected_stage"],"known_ids":root["known_ids"],
                      "raw_prompt":raw,"raw_public_view":view,"normalized_public_view":normal,"normalized_prompt":normalized})
        for repeat in range(2):
            frozen=next(r for r in evaluations if r["root_id"]==root["root_id"] and r["repeat"]==repeat)
            assert frozen["prompt"]==raw and set(frozen["known_ids"])==set(ids)
            arms=("raw","normalized") if (index+repeat)%2==0 else ("normalized","raw")
            for arm in arms:
                call={"root_id":root["root_id"],"width":root["width"],"repeat":repeat,"arm":arm,"kind":"selection","seed":frozen["seed"],"max_tokens":384}
                key=study.call_id(call);prompt=raw if arm=="raw" else normalized;request=study.request_body(prompt,frozen["seed"],384)
                if arm=="raw":assert request==frozen["request"]
                calls.append(call);prompts[key]=prompt;requests[key]=request
                audit.append({"call_id":key,"root_id":root["root_id"],"arm":arm,"seed":frozen["seed"],"input_tokens":len(request["token_ids"]),"prefix_sha256":study.digest(request["token_ids"]),"all_original_ids_retained":True})
    # The public payload is fixed before host gold is opened. Normalizer imports no study/solver or files.
    study.write_x(study.INPUTS,{"schema":"b05-held9-raw-vs-public-normalized-native36-plan-v1","tasks":tasks,"calls":calls,"prompts":prompts,"requests":requests})
    host=[r for r in study.read(study.TRAIN/"HOST_GOLD.json")["rows"] if r["split"]=="held"]
    assert len(host)==9 and {r["root_id"] for r in host}=={t["root_id"] for t in tasks}
    study.write_x(study.HOST,{"rows":host,"source":str(study.TRAIN/"HOST_GOLD.json"),"normalizer_did_not_read_gold":True})
    study.write_x(study.ROOT/"TOKEN_AUDIT.json",{"rows":audit})
    command=[str(study.NATIVE),"-m","pytest","-q","test_normalize.py","--basetemp=cpu-fixture-seal-001"]
    result=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True)
    study.write_x(study.ROOT/"CPU_TESTS.json",{"command":command,"returncode":result.returncode,"stdout":result.stdout,"stderr":result.stderr,"GPU_calls":0,"model_calls":0,"actual_frozen_pair_HTTP":True})
    assert result.returncode==0,result.stdout+result.stderr
    owner.implementation()
    closure=dict(study.read(study.SERVICE_READY)["closure_sha256"])
    paths=list(study.ROOT.glob("*.py"))+[study.ROOT/"RUNBOOK.md",study.INPUTS,study.HOST,study.ROOT/"TOKEN_AUDIT.json",study.ROOT/"CPU_TESTS.json",
          study.TRAIN/"READY.json",study.TRAIN/"HELD_PUBLIC.json",study.TRAIN/"EVAL_TASKS.json",study.TRAIN/"HOST_GOLD.json",study.SERVICE_READY,
          study.SERVICE_READY.parent/"outputs/attempt-001/OWNER_TERMINAL.json",study.SERVICE_READY.parent/"outputs/attempt-001/RESULT.json"]
    for path in paths+list((study.ROOT/"cpu-fixture-seal-001").rglob("*.json")):closure[str(path)]=study.sha(path)
    ready={"schema":"b05-public-mechanical-normalization-held9-ready-v1","status":"CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION","created_utc":datetime.now(timezone.utc).isoformat(),
           "argv":[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--outer-seconds","700"],"launch_authority":"MAIN only",
           "context_units":9,"paired_seed_units":18,"planned_physical_calls":36,"arms":["raw","normalized"],"new_raw_controls":True,
           "same_held9_and_seed_pairs_as_selection_RL":True,"seeds":[202609330000,202609330017],"same_model_prompt_output_contract_except_input_normalization":True,
           "model":str(study.MODEL),"model_alias":study.MODEL_ALIAS,"adapter":None,"temperature":.5,"max_tokens":384,"input_cap":8192,
           "owner_seconds":700,"science_seconds":600,"external_seconds":800,"input_token_max":max(r["input_tokens"] for r in audit),
           "input_token_max_by_arm":{a:max(r["input_tokens"] for r in audit if r["arm"]==a) for a in ("raw","normalized")},
           "primary":"unordered known unique-ID exact; BA precision recall on explicit valid-set denominator","strict_sorted_format_separate":True,"unknown_is_not_wrong":True,
           "normalizer":"public applied numeric deltas, union additions minus all removals, latest required checks, ALL candidates retained",
           "normalizer_computes_eligibility":False,"normalizer_reads_host_gold":False,"normalizer_filters_candidates":False,"no_hidden_eligibility_or_root_answer":True,
           "input_representation_and_explanatory_instruction_jointly_change":True,"natural_calls_per_answer":1,"token_costs_not_matched":True,"not_learned_decomposition":True,
           "record_response_sha256_semantics":"canonical parsed JSON digest; original response bytes retained separately",
           "source_service_ready_sha256":study.SERVICE_SHA,"held_data_ready_sha256":study.DATA_SHA,"closure_sha256":dict(sorted(closure.items()))}
    ready["identity"]=study.digest(ready);study.write_x(study.READY_RUN,ready);study.verify()
    print(json.dumps({"ready":str(study.READY_RUN),"sha256":study.sha(study.READY_RUN),"identity":ready["identity"],"max_tokens_by_arm":ready["input_token_max_by_arm"],"closure_files":len(closure)}))


if __name__=="__main__":main()
