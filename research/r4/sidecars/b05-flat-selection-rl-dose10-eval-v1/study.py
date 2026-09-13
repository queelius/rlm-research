"""Original72 evaluator with only the fixed qualified dose10 endpoint substituted."""
import hashlib
from pathlib import Path
PARENT=Path(__file__).resolve().parent.parent/'b05-flat-selection-rl-eval-v1'
assert hashlib.sha256((PARENT/'READY.json').read_bytes()).hexdigest()=='a32cae2ac08ec93327805eef6afc886e8f15e20fd00361bff90488db614b2d52'
# __file__ remains this additive entrypoint, so inherited ROOT/READY/ATTEMPT are new.
exec(compile((PARENT/'study.py').read_text(),str(PARENT/'study.py'),'exec'),globals())
DOSE=ROOT.parent/'b05-flat-selection-rl-dose10-v1'
train=load('BA18_dose_readout_training',DOSE/'study.py')
# TRAIN deliberately remains original data location; no task/data files are regenerated.

def checkpoint():
    with aliases({'study':train},DOSE):
        core=load('BA18_dose_readout_core',DOSE/'core.py')
        with aliases({'core':core},DOSE):
            value=load('BA18_dose_readout_checkpoint',DOSE/'checkpoint.py').endpoint()
    assert value['learning_rate']==1e-3 and value['exact_original_zero_B_initialization']
    return value
