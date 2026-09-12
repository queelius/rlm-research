"""Frozen ten-case AnomalyXL budget-shape follow-up over the sealed V1 interface."""

import functools
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT=Path(__file__).resolve().parent
V1=ROOT.parent/"anomalyxl-native-mini-v1"
ATTEMPT=ROOT/"outputs/attempt-001"
CAP,EPISODE_CAP,TOTAL_OUTPUT=1800,90,2048
NATIVE=Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load "+str(path))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


base=load("anomalyxl_budget_v1_sealed",V1/"mini.py")
base.ATTEMPT=ATTEMPT
read=base.read;sha=base.sha;digest=base.digest;write=base.write
body=base.body;decode=base.decode;executor=base.executor;execute_cell=base.execute_cell
observation=base.observation;score=base.score


def panel(): return read(V1/"inputs/PANEL.json")


def schedule():
    arms=("direct","python_wide1","python_repair3");rows=[]
    for index,row in enumerate(panel()):
        order=arms[index%3:]+arms[:index%3]
        rows.extend({"episode_id":f"{index:02d}-{arm}","row_id":row["id"],"arm":arm,"panel_index":index} for arm in order)
    return rows


def allowance(arm,generated,final):
    remaining=TOTAL_OUTPUT-generated
    if remaining<=0: raise ValueError("aggregate output budget exhausted")
    if final: return remaining
    if arm=="python_wide1": return min(1536,remaining)
    if arm=="python_repair3": return min(512,remaining)
    raise ValueError("inspection allowance requires Python arm")


def inspection_prompt(question,arm):
    turns=1 if arm=="python_wide1" else 3
    return (
        "The full numerical data is in context.json in your working directory, shaped "
        '{"series": {channel: [values]}}. Read actual channel names. Values are rounded to '
        "3 decimals; indices are original sample indices. Use NumPy or the Python standard "
        "library (SciPy is not installed), without images, plots, network, shell commands, "
        f"child models or other files. You have exactly {turns} inspection turn(s), followed "
        "by one final answer. Return exactly one fenced python cell, no prose. Fit a complete "
        "executable cell within this turn's token limit: prioritize compact computation and "
        "concise printed observations. Do not call final() or submit an answer in the cell.\n"
        "Question: "+question
    )


def verify():
    ready=read(ROOT/"READY.json")
    for path,expected in ready["closure_sha256"].items():
        if sha(path)!=expected: raise ValueError("sealed source changed: "+path)
    if schedule()!=ready["schedule"]: raise ValueError("schedule changed")
    return ready
