"""Native scoring reuse and explicit single/agreement-abstain derivation."""
import importlib.util
from pathlib import Path

SOURCE=Path(__file__).parent.parent/"root-supplied-plan-selective-recheck-v1/protocol.py"
spec=importlib.util.spec_from_file_location("taskaware_base_protocol",SOURCE)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
CATEGORIES=base.CATEGORIES;score=base.score;native=base.native;reduce_j1=base.reduce_j1

def _status(rows):
    if any(not r["score"]["available"] for r in rows):return "null"
    if any(not r["score"]["complete_map"] for r in rows):return "observed_invalid"
    return "valid"

def derive_single(baseline,rows_a):
    status=_status(rows_a)
    if status!="valid":return {"status":status,"available":status!="null","valid":False,"labels":None}
    labels=dict(baseline);selected=set()
    for row in rows_a:
        assert row["coordinate"]["sample"]=="A" and not selected.intersection(row["score"]["labels"])
        selected.update(row["score"]["labels"]);labels.update(row["score"]["labels"])
    return {"status":"valid","available":True,"valid":True,"labels":labels,"overwritten":len(selected)}

def derive_agreement(baseline,rows_a,rows_b):
    status=_status(rows_a+rows_b)
    if status!="valid":return {"status":status,"available":status!="null","valid":False,"labels":None}
    a={k:v for row in rows_a for k,v in row["score"]["labels"].items()}
    b={k:v for row in rows_b for k,v in row["score"]["labels"].items()}
    if set(a)!=set(b):raise ValueError("A/B selected inventory mismatch")
    labels=dict(baseline);agreed={k:v for k,v in a.items() if v==b[k]};labels.update(agreed)
    return {"status":"valid","available":True,"valid":True,"labels":labels,
            "overwritten":len(agreed),"abstentions":len(a)-len(agreed),
            "agreements":len(agreed)}

