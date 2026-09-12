"""Pinned evaluator reuse; changes are names, training metadata and data routing."""
import hashlib
from pathlib import Path

PREVIOUS=Path(__file__).resolve().parent.parent/"helper-agnews-eightstep-seed2-eval-v1"
PINS={
    "bundle.py":"a04d9838332ca9ee21092090212775296b76ec125afcc9548a34e2eb1fb8c959",
    "owner.py":"293124dbe2cd037cad99ad3c74510972540463198de84bfbfdfb58ca072b2b54",
    "compare.py":"f3a59fae9f4162079e13d5c715fe5cdab487130dc507fe675e7d4890eaf557ad",
}


def execute(name,scope,replacements=()):
    path=PREVIOUS/name;raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PINS[name]:raise ValueError("reviewed evaluator changed: "+name)
    text=raw.decode()
    for before,after,count in replacements:
        if text.count(before)!=count:raise ValueError("exact repeated-eval metadata seam differs: "+before)
        text=text.replace(before,after)
    exec(compile(text,str(path),"exec"),scope)
