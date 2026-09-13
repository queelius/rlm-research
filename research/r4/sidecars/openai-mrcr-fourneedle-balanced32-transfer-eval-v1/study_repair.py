"""Additive service-boundary repair: use the proven dual-LoRA eval dependency."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('balanced32_v1_study_for_repair',ROOT/'study.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
for name in dir(base):
    if not name.startswith('_') and name!='dependencies':globals()[name]=getattr(base,name)
def dependencies():
    return eval_study().dependencies()
