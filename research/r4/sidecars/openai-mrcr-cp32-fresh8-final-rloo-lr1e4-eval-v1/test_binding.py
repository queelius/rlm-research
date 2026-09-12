"""New LR binding cannot silently accept the old LR1e-5 checkpoint metadata."""
from pathlib import Path
import importlib
import copy
import pytest

def test_actual_lr1e4_checkpoint_and_reject_old_lr():
    assert (Path(__file__).parent/'checkpoint.py').exists(), 'dose evaluator not implemented'
    s=importlib.import_module('study');c=importlib.import_module('checkpoint')
    q=c.verify_checkpoint();assert q['eligible'] and q['replay_actions']==12 and q['zero_advantage_skipped']==20
    state=s.read(c.CHECKPOINT/'state.json');binding=c.binding('updated')
    assert state['learning_rate']==1e-4 and binding['role_map']['root']==s.ADAPTED_ALIAS
    bad=copy.deepcopy(state);bad['learning_rate']=1e-5
    with pytest.raises(AssertionError):c.validate_state_binding(bad,binding)
    assert s.schedule('train')==s.trainread.schedule('train') and len(s.schedule('train'))==32
    assert s.schedule('held')==s.prior.schedule('held') and len(s.schedule('held'))==32
