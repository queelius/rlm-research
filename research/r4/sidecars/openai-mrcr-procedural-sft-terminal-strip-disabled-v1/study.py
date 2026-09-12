"""Exact completed cp32 held schedule, prompts, runtime and compute settings."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'openai-mrcr-procedural-sft-continue32-eval-v1'
READY=ROOT/'CPU_READY.json'

spec=importlib.util.spec_from_file_location('terminal_strip_previous_study',PRIOR/'study.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
for name in dir(previous):
    if not name.startswith('_') and name not in {'ROOT','READY','PRIOR'}:
        globals()[name]=getattr(previous,name)

BASELINE=PRIOR/'outputs/held-checkpoint32-001'
TRAIN_READOUT=PRIOR/'outputs/train32-001'

