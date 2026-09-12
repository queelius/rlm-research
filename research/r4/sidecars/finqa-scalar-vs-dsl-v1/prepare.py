"""Freeze public16/host targets and native32 inputs, test, seal; no model service."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import owner
import science
import study


def main():
    assert not study.READY_RUN.exists()
    data=study.read(study.DATA)
    ranked=sorted(data,key=lambda row:(hashlib.sha256((study.REV+"\n"+row["id"]).encode()).hexdigest(),row["id"]))
    contexts=[];targets=[];seen=set();calls=[];prompts={};audits=[]
    annotation_path=study.ROOT.parents[1] / "analyses/finqa-reference-interface-feasibility-2026-09-12/ANNOTATION_CONSISTENCY.json"
    flags={row["id"]:row["written_answer_vs_execution_target"] for row in study.read(annotation_path)["rows"]}
    for row in ranked:
        if row["filename"] in seen:continue
        seen.add(row["filename"])
        index=len(contexts)
        public={"question":row["qa"]["question"],"pre_text":row["pre_text"],"post_text":row["post_text"],"table":row["table"]}
        rank=hashlib.sha256((study.REV+"\n"+row["id"]).encode()).hexdigest()
        contexts.append({"id":row["id"],"filename":row["filename"],"rank_sha256":rank,"public":public})
        ops=re.findall(r"([a-z_]+)\(",row["qa"]["program"])
        targets.append({"id":row["id"],"exe_ans":row["qa"]["exe_ans"],"written_answer":row["qa"]["answer"],
                        "gold_program_inert":row["qa"]["program"],"annotation_flag":flags[row["id"]],
                        "supported_gold_op_names":set(ops)<=set(science.OPS),"gold_steps":len(ops)})
        for arm in ("direct_scalar","restricted_dsl"):
            call={"kind":arm,"context_index":index,"example_id":row["id"],"seed":202609290000+index,"max_tokens":384}
            call_id=study.call_id(call);prompt=science.prompt(public,arm)
            request=study.request_body(prompt,call["seed"],384)
            calls.append(call);prompts[call_id]=prompt
            audits.append({"call_id":call_id,"example_id":row["id"],"arm":arm,"seed":call["seed"],
                           "request":request,"input_tokens":len(request["token_ids"]),
                           "prefix_token_ids_sha256":study.digest(request["token_ids"]),"shared_public_sha256":study.digest(public)})
        if len(contexts)==16:break
    assert len(contexts)==16 and len(calls)==32
    study.write_x(study.INPUTS,{"schema":"finqa-fixed16-public-native-plan-v1","revision":study.REV,
                  "selection":"ascending SHA256(revision+LF+id), first16 distinct page filenames; no outcome/annotation filtering",
                  "contexts":contexts,"calls":calls,"prompts":prompts})
    study.write_x(study.HOST,{"schema":"finqa-fixed16-host-only-targets-v1","contexts":targets,
                  "all16_retained":True,"targets_and_programs_not_in_prompts":True})
    study.write_x(study.ROOT / "TOKEN_AUDIT.json",{"schema":"finqa32-actual-native-input-token-audit-v1","calls":audits})
    command=[str(study.NATIVE),"-m","pytest","-q","test_science.py","--basetemp=cpu-fixture-seal-001"]
    tested=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True)
    test_path=study.ROOT / "CPU_TESTS.json"
    study.write_x(test_path,{"command":command,"returncode":tested.returncode,"stdout":tested.stdout,"stderr":tested.stderr,
                            "model_calls":0,"GPU_calls":0,"full_paired_HTTP_fixture":True})
    assert tested.returncode==0
    owner.implementation()
    assert study.sha(study.SOURCE_READY)==study.SOURCE_READY_SHA
    closure=dict(study.read(study.SOURCE_READY)["closure_sha256"])
    for path in sorted(study.ROOT.glob("*.py"))+[study.ROOT / "RUNBOOK.md",study.INPUTS,study.HOST,test_path,study.ROOT / "TOKEN_AUDIT.json",
                 study.SOURCE_READY,study.SOURCE / "outputs/attempt-003/OWNER_TERMINAL.json",study.SOURCE / "outputs/attempt-003/RESULT.json",
                 study.DATA,study.DATA.parent.parent / "LICENSE",study.DATA.parent.parent / "README.md",
                 study.DATA.parent.parent / "code/evaluate/evaluate.py",annotation_path,
                 Path("/project/alex_phd/research-cache/datasets") / ("finqa-"+study.REV) / "ACQUISITION_MANIFEST.json"]:
        closure[str(path)]=study.sha(path)
    ready={"schema":"finqa-scalar-vs-restricted-dsl-ready-v1","status":"CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION",
           "created_utc":datetime.now(timezone.utc).isoformat(),"data_revision":study.REV,"split":"official dev",
           "planned_physical_calls":32,"paired_context_units":16,"owner_seconds":700,"science_seconds":600,"external_seconds":800,
           "argv":[str(study.NATIVE),str(study.ROOT / "owner.py"),"run","--outer-seconds","700"],
           "arms":["direct_scalar","restricted_dsl"],"temperature":.5,"max_tokens_each":384,"same_seed_per_pair":True,
           "all10_ops_supported":True,"five_step_cap":True,"selected_gold_op_coverage":sum(row["supported_gold_op_names"] for row in targets),
           "selected_gold_step_cap_coverage":sum(row["gold_steps"]<=5 for row in targets),
           "no_outcome_or_annotation_filter":True,"no_gold_in_model_prompts":True,"no_generation_or_training_during_prep":True,
           "metric":"provided FinQA exe_ans equality after prediction round5; % literals divide100; no gold-based scale fix",
           "not_official_program_generation_metric":True,"not_semantic_truth_or_recursion_claim":True,
           "model_output_interpreter_uses_no_eval_exec":True,"trusted_owner_compilation_is_not_model_program_execution":True,
           "record_response_sha256_semantics":"canonical parsed JSON digest; raw response file is retained and independently hashable",
           "licenses":{"repository":"MIT","official_dataset_site":"CC BY4.0","underlying_FinTabNet":"CDLA-Permissive"},
           "launch_authority":"MAIN only","closure_sha256":dict(sorted(closure.items()))}
    ready["identity"]=study.digest(ready)
    study.write_x(study.READY_RUN,ready)
    study.verify()
    print(json.dumps({"ready":str(study.READY_RUN),"sha256":study.sha(study.READY_RUN),"identity":ready["identity"],
                      "tokens_max":max(row["input_tokens"] for row in audits),"gold_ops_covered":ready["selected_gold_op_coverage"]}))


if __name__=="__main__":main()
