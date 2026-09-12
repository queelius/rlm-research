from pathlib import Path
import importlib
import math
import pytest

ROOT=Path(__file__).resolve().parent
def module():
    assert (ROOT/'analyze.py').exists(), 'fresh RLOO analyzer not implemented'
    return importlib.import_module('analyze')

def test_actual_new_seed_cp32_raw_control_binding_and_score():
    a=module();r=a.stage('held','cp32')
    assert r['available']==r['planned']==32 and r['correct']==25
    assert r['qualified'] and not r['integrity_errors']
    assert r['initial_prefix_verified']==32 and r['physical']['start_only']==0
    assert sorted(x['coordinate']['seed'] for x in r['rows'].values())==list(range(202609270000,202609270032))
    assert r['physical']['orphan_returned']==0

def test_preclip_components_are_scaled_before_saved_gradient_subtraction():
    module();g=importlib.import_module('gradient')
    import torch
    factor=1/(5+1e-6)
    post={'p':torch.tensor([3.,4.],dtype=torch.float64)*factor}
    negative={'whitespace':{'p':torch.tensor([1.,0.],dtype=torch.float64)},
              'eos':{'p':torch.tensor([0.,1.],dtype=torch.float64)},
              'body':{'p':torch.zeros(2,dtype=torch.float64)}}
    parts,summary=g.decompose(post,negative,5.)
    assert summary['clip_factor']==pytest.approx(factor)
    assert torch.allclose(parts['positive_residual']['p'],torch.tensor([2.,3.],dtype=torch.float64)*factor)
    assert summary['components']['positive_residual']['preclip_l2_inferred']==pytest.approx(math.sqrt(13))
    assert summary['components']['negative_whitespace']['postclip_l2']==pytest.approx(factor)
    assert summary['reconstruction_max_abs_error']<1e-12
