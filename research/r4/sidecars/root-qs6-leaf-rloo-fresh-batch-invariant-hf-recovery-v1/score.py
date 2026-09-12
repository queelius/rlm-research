"""HF target scorer consuming only precomputed, authenticated xgrammar masks."""

import argparse
import importlib.util
import json
from pathlib import Path

import study


def precomputed_records(collection,directory,_leaf_math,_prepare):
    if Path(directory).resolve()!=(study.ATTEMPT/"qualification-inputs").resolve():raise ValueError("unexpected prepared directory")
    prepared=study.read(study.ATTEMPT/"PREPARED.json");dataset=study.read(directory/"DATASET.json");manifest=study.read(directory/"MASK_MANIFEST.json")
    checks={"dataset_sha256":study.sha(directory/"DATASET.json"),"mask_manifest_sha256":study.sha(directory/"MASK_MANIFEST.json"),"masks_sha256":study.sha(directory/"MASKS.npz"),"collection_sha256":study.sha(study.ATTEMPT/"COLLECTION.json")}
    if any(prepared.get(k)!=v for k,v in checks.items()) or manifest.get("dataset_sha256")!=checks["dataset_sha256"] or manifest.get("masks_npz_sha256")!=checks["masks_sha256"]:raise ValueError("precomputed artifact identity differs")
    if collection!=study.read(study.ATTEMPT/"COLLECTION.json") or len(dataset.get("records",[]))!=48:raise ValueError("precomputed record inventory differs")
    source={row["coordinate_id"]:row for row in collection["records"]}
    for row in dataset["records"]:
        original=source.get(row["coordinate_id"])
        if original is None or any(row.get(k)!=v for k,v in original.items()):raise ValueError("prepared record differs from fresh V2 action")
    return dataset,dataset["records"],manifest


def module():
    path=study.SIDE/"root-qs6-leaf-rloo-fresh-batch-invariant-qualification-v1/qualify.py";spec=importlib.util.spec_from_file_location("hf_recovery_v1_qualifier",path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    value.study=study;value.prepare_records=precomputed_records
    return value


def verify_only():
    base=module();collection=study.read(study.ATTEMPT/"COLLECTION.json");dataset,records,manifest=precomputed_records(collection,study.ATTEMPT/"qualification-inputs",None,None)
    return {"status":"PRECOMPUTED_INPUTS_VERIFIED_WITHOUT_XGRAMMAR","records":len(records),"masks_sha256":manifest["masks_npz_sha256"],"optimizer_steps":0}


def main(run=False):
    if not run:print(json.dumps(verify_only(),sort_keys=True));return
    base=module();result=base.run(study.ATTEMPT,study.CAP,study.SOURCE_ATTEMPT/"service/SERVICE_STOPPED.json");print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--run",action="store_true");main(parser.parse_args().run)
