"""BA18 exact original-start, same frozen actions, sole10x-LR dose contrast."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent;ORIGINAL=ROOT.parent/'b05-flat-selection-rl-v1'
spec=importlib.util.spec_from_file_location('BA18_dose_original_study',ORIGINAL/'study.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
for name in ('read','sha','digest','write_x','bytes_x','load','aliases','STORE','WIDTH','width','PRIOR','OLD',
    'BASE','NATIVE','PYTHON','INPUTS','CONFIG_SOURCE','INIT_SEED','SEED','NP_SEED','DENOMINATOR','TEMPERATURE',
    'TOKEN_TIS_CAP','SCIENCE_SECONDS','OWNER_SECONDS','EXTERNAL_SECONDS','positions_and_targets','reward','array_mask','validate_inputs'):
    globals()[name]=getattr(original,name)
READY=ROOT/'READY.json';OUTPUT=ROOT/'outputs/attempt-001'
LEARNING_RATE=1e-3;ALIAS='Qwen3-4B-Instruct-2507-b05-flat-BA18-dose10-step1'
INITIAL_REFERENCE=original.OUTPUT/'initial-trainable.pt'

def verify():
    ready=read(READY);assert ready['identity']==digest({k:v for k,v in ready.items() if k!='identity'})
    for p,h in ready['closure_sha256'].items():assert sha(p)==h,p
    assert LEARNING_RATE==10*original.LEARNING_RATE and INPUTS==original.INPUTS
    assert (INIT_SEED,SEED,NP_SEED)==(original.INIT_SEED,original.SEED,original.NP_SEED)
    validate_inputs(read(INPUTS));return ready
