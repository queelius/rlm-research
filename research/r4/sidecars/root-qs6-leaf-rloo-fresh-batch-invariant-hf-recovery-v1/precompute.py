"""Use the native CPU environment once to build exact xgrammar masks for saved V2 actions."""

import copy
import importlib
import json
import math
from pathlib import Path
import sys

import study


def validate_source():
    ready=study.read(study.SOURCE/"READY.json");terminal=study.read(study.SOURCE_ATTEMPT/"OWNER_TERMINAL.json")
    if study.sha(study.SOURCE/"READY.json")!="53a379c03a5acb9e04113a0a866c7c734dd1ad62454ba0658b71f81287e8454b" or ready["identity"]!="b27457638bfdeaae7b3edbbb12dddff44c0eb9b04a29287f50f3056bd960c346":raise ValueError("unexpected V2 source")
    stderr=(study.SOURCE_ATTEMPT/"HF_QUALIFIER.stderr.log").read_text()
    if terminal.get("complete") is not False or terminal.get("released_before_hf") is not True or terminal.get("optimizer_steps")!=0 or not any(error.get("stage")=="hf_qualification" for error in terminal.get("errors",[])) or "ModuleNotFoundError: No module named 'xgrammar'" not in stderr:raise ValueError("source is not exact post-collection xgrammar failure")
    stopped=study.read(study.SOURCE_ATTEMPT/"service/SERVICE_STOPPED.json")
    if stopped.get("all_owned_process_identities_exited") is not True or stopped.get("ports_free") is not True:raise ValueError("source service not released")
    collection=study.read(study.SOURCE_ATTEMPT/"COLLECTION.json")
    if collection.get("fresh_actions")!=48 or collection.get("historical_actions_or_logprobs_used") is not False or len(collection.get("records",[]))!=48:raise ValueError("source collection differs")
    inventory={}
    for record in collection["records"]:
        for key in ("raw_request_path","raw_response_path"):
            path=Path(record[key]);expected=record[key.replace("path","sha256")]
            if study.sha(path)!=expected:raise ValueError("raw source differs")
            inventory[str(path)]=expected
        call=study.SOURCE_ATTEMPT/"calls"/(record["coordinate_id"]+".json")
        if study.read(call)!=record:raise ValueError("call/collection differs")
        inventory[str(call)]=study.sha(call)
        if len(record["action_ids"])!=len(record["old_logprobs"]) or not all(math.isfinite(x) for x in record["old_logprobs"]):raise ValueError("behavior likelihood differs")
    return ready,terminal,collection,inventory


def main():
    if study.ATTEMPT.exists():raise FileExistsError("recovery attempt exists; refusing rebuild")
    _,terminal,collection,inventory=validate_source();study.ATTEMPT.mkdir(parents=True)
    study.write_x(study.ATTEMPT/"COLLECTION.json",collection)
    records=copy.deepcopy(collection["records"]);sys.path.insert(0,str(study.V1))
    leaf_math=importlib.import_module("leaf_math");prepare=importlib.import_module("prepare")
    advantages=leaf_math.rloo_advantages([r["reward"] for r in records],[r["group_id"] for r in records],reward_scale=16)
    for record,advantage in zip(records,advantages,strict=True):record["advantage"]=advantage
    inputs=study.ATTEMPT/"qualification-inputs";manifest=prepare.generate_masks(records,inputs)
    dataset={"schema":"fresh-batch-invariant-hf-recovery-dataset-v1","status":"precomputed_native_cpu_no_optimizer","model":{"base":str(study.BASE_MODEL),"base_config_sha256":study.sha(study.BASE_MODEL/"config.json"),"child_start":str(study.CHILD_START),"child_adapter_sha256":study.sha(study.CHILD_START/"adapter_model.safetensors"),"child_adapter_config_sha256":study.sha(study.CHILD_START/"adapter_config.json")},"objective":{"temperature":0.5,"ess_min":38.4,"max_normalized_weight":0.1},"inventory":{"episodes":48,"groups":2,"group_sizes":[24,24],"action_tokens":sum(len(r["action_ids"]) for r in records)},"records":records}
    study.write_x(inputs/"DATASET.json",dataset);manifest.update(dataset=str(inputs/"DATASET.json"),dataset_sha256=study.sha(inputs/"DATASET.json"));study.write_x(inputs/"MASK_MANIFEST.json",manifest)
    study.write_x(study.ATTEMPT/"SOURCE_INVENTORY.json",{"source_v2_collection":str(study.SOURCE_ATTEMPT/"COLLECTION.json"),"source_v2_collection_sha256":study.sha(study.SOURCE_ATTEMPT/"COLLECTION.json"),"source_v2_terminal_sha256":study.sha(study.SOURCE_ATTEMPT/"OWNER_TERMINAL.json"),"source_service_stopped_sha256":study.sha(study.SOURCE_ATTEMPT/"service/SERVICE_STOPPED.json"),"raw_and_call_sha256":inventory,"v1_raw_responses_reused":False,"v2_actions_recollected":False})
    study.write_x(study.ATTEMPT/"PREPARED.json",{"status":"CPU_MASKS_PRECOMPUTED","optimizer_steps":0,"source_failure_stage":"HF mask generation environment boundary","dataset_sha256":study.sha(inputs/"DATASET.json"),"mask_manifest_sha256":study.sha(inputs/"MASK_MANIFEST.json"),"masks_sha256":study.sha(inputs/"MASKS.npz"),"collection_sha256":study.sha(study.ATTEMPT/"COLLECTION.json"),"source_terminal_elapsed_seconds":terminal["elapsed_seconds"]})
    print(json.dumps(study.read(study.ATTEMPT/"PREPARED.json"),sort_keys=True))


if __name__=="__main__":main()
