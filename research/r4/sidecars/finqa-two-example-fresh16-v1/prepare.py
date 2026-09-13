"""Freeze next16 distinct dev pages after excluding original16; CPU only."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import interface
import owner
import study


def main():
    assert not study.READY_RUN.exists()
    assert study.sha(study.PRIOR_READY)==study.PRIOR_READY_SHA
    excluded={r["filename"] for r in study.read(study.PRIOR/"PUBLIC_INPUTS.json")["contexts"]}
    data=study.read(study.DATA)
    ranked=sorted(data,key=lambda r:(hashlib.sha256((study.REV+"\n"+r["id"]).encode()).hexdigest(),r["id"]))
    selected=[];seen=set()
    # Selection deliberately precedes reading any target/annotation fields.
    for row in ranked:
        if row["filename"] in excluded or row["filename"] in seen:continue
        selected.append(row);seen.add(row["filename"])
        if len(selected)==16:break
    assert len(selected)==16 and not seen&excluded
    annotations=study.ROOT.parents[1]/"analyses/finqa-reference-interface-feasibility-2026-09-12/ANNOTATION_CONSISTENCY.json"
    flags={r["id"]:r["written_answer_vs_execution_target"] for r in study.read(annotations)["rows"]}
    contexts=[];targets=[];calls=[];prompts={};audits=[]
    for index,row in enumerate(selected):
        public={"question":row["qa"]["question"],"pre_text":row["pre_text"],"post_text":row["post_text"],"table":row["table"]}
        contexts.append({"id":row["id"],"filename":row["filename"],"rank_sha256":hashlib.sha256((study.REV+"\n"+row["id"]).encode()).hexdigest(),"public":public})
        ops=re.findall(r"([a-z_]+)\(",row["qa"]["program"])
        targets.append({"id":row["id"],"exe_ans":row["qa"]["exe_ans"],"written_answer":row["qa"]["answer"],
                        "gold_program_inert":row["qa"]["program"],"annotation_flag":flags[row["id"]],
                        "supported_gold_op_names":set(ops)<=set(study.science.OPS),"gold_steps":len(ops)})
        for arm in ("direct_scalar","restricted_dsl"):
            call={"kind":arm,"context_index":index,"example_id":row["id"],"seed":study.SEED_BASE+index,"max_tokens":384}
            key=study.call_id(call);prompt=interface.prompt(public,arm);request=study.request_body(prompt,call["seed"],384)
            calls.append(call);prompts[key]=prompt
            audits.append({"call_id":key,"example_id":row["id"],"arm":arm,"seed":call["seed"],"request":request,
                           "input_tokens":len(request["token_ids"]),"prefix_token_ids_sha256":study.digest(request["token_ids"]),"shared_public_sha256":study.digest(public)})
    rule="ascending SHA256(revision+LF+id), first16 distinct page filenames after excluding every original16 filename; no annotation/op/difficulty/outcome filter"
    study.write_x(study.INPUTS,{"schema":"finqa-next16-two-example-public-native-plan-v1","revision":study.REV,"selection":rule,
                  "excluded_prior_filenames":sorted(excluded),"contexts":contexts,"calls":calls,"prompts":prompts,"synthetic_facts_questions":interface.FACTS})
    study.write_x(study.HOST,{"schema":"finqa-fresh16-host-only-targets-v1","contexts":targets,"all16_retained":True,"targets_and_programs_not_in_prompts":True})
    study.write_x(study.ROOT/"TOKEN_AUDIT.json",{"schema":"finqa-fresh16-actual-native32-token-audit-v1","calls":audits})
    cmd=[str(study.NATIVE),"-m","pytest","-q","test_fresh.py","--basetemp=cpu-fixture-seal-001"]
    tested=subprocess.run(cmd,cwd=study.ROOT,capture_output=True,text=True)
    study.write_x(study.ROOT/"CPU_TESTS.json",{"command":cmd,"returncode":tested.returncode,"stdout":tested.stdout,"stderr":tested.stderr,"actual_fresh_pair_HTTP":True,"GPU_calls":0,"model_calls":0})
    assert tested.returncode==0,tested.stdout
    owner.implementation()
    prior_ready=study.read(study.PRIOR_READY);closure=dict(prior_ready["closure_sha256"])
    paths=list(study.ROOT.glob("*.py"))+[study.ROOT/"RUNBOOK.md",study.INPUTS,study.HOST,study.ROOT/"TOKEN_AUDIT.json",study.ROOT/"CPU_TESTS.json",study.PRIOR_READY,
          study.PRIOR/"outputs/attempt-001/RESULT.json",study.PRIOR/"outputs/attempt-001/OWNER_TERMINAL.json",study.DATA,annotations]
    for path in paths+list((study.ROOT/"cpu-fixture-seal-001").rglob("*.json")):closure[str(path)]=study.sha(path)
    ready={"schema":"finqa-next16-identical-two-example-replication-ready-v1","status":"CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION",
           "created_utc":datetime.now(timezone.utc).isoformat(),"launch_authority":"MAIN only",
           "argv":[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--outer-seconds","700"],
           "data_revision":study.REV,"split":"official dev","selection":rule,"excluded_prior_filenames":sorted(excluded),
           "planned_physical_calls":32,"paired_context_units":16,"seed_namespace":[study.SEED_BASE,study.SEED_BASE+15],
           "same_seed_within_pair":True,"new_pages_and_seed_namespace_not_matched_old_panel":True,
           "owner_seconds":700,"science_seconds":600,"external_seconds":800,"temperature":.5,"max_tokens_each":384,"input_cap":8192,
           "model":str(study.MODEL),"model_alias":study.MODEL_ALIAS,"adapter":None,"arms":["direct_scalar","restricted_dsl"],
           "model_input_token_max":max(r["input_tokens"] for r in audits),"five_step_cap":True,"all10_ops_supported":True,
           "selected_gold_op_coverage_diagnostic_only":sum(r["supported_gold_op_names"] for r in targets),
           "selected_gold_step_cap_coverage_diagnostic_only":sum(r["gold_steps"]<=5 for r in targets),
           "prior_ready_sha256":study.PRIOR_READY_SHA,"prior_result_sha256":study.PRIOR_RESULT_SHA,
           "same_two_example_builder_and_interpreter":True,"no_new_prompt_variant":True,"no_gold_in_prompts":True,
           "no_outcome_annotation_or_operator_filter":True,"provided_target_not_semantic_truth":True,"not_weight_learning_or_novel_method":True,
           "metric":prior_ready["metric"],"licenses":prior_ready["licenses"],"record_response_sha256_semantics":prior_ready["record_response_sha256_semantics"],
           "natural_calls_per_answer_each_arm":1,"token_costs_not_matched":True,"closure_sha256":dict(sorted(closure.items()))}
    ready["identity"]=study.digest(ready);study.write_x(study.READY_RUN,ready);study.verify()
    print(json.dumps({"ready":str(study.READY_RUN),"sha256":study.sha(study.READY_RUN),"identity":ready["identity"],"max_input":ready["model_input_token_max"],"closure_files":len(closure)}))


if __name__=="__main__":main()
