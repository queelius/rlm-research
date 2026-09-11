import torch
import diagnostic_math as dm
import diagnostic_owner as owner


def test_float64_metrics_are_exact_for_identical_vectors():
    a=torch.tensor([1e8,1.0,-1e8,3.0],dtype=torch.float32)
    result=dm.compare(a,a.clone(),chunk=2)
    assert result["relative_l2"] == 0.0
    assert abs(result["cosine"]-1.0) < 1e-15


def test_float64_metrics_match_direct_double_reference():
    a=torch.tensor([1.,2.,3.,4.],dtype=torch.float32); b=a+torch.tensor([0.,.1,0.,-.2])
    result=dm.compare(a,b,chunk=2); ad=a.double();bd=b.double()
    assert abs(result["relative_l2"]-float(torch.linalg.vector_norm(ad-bd)/torch.linalg.vector_norm(ad)))<1e-14
    assert abs(result["cosine"]-float(torch.dot(ad,bd)/(torch.linalg.vector_norm(ad)*torch.linalg.vector_norm(bd))))<1e-14


def test_owner_is_single_no_optimizer_diagnostic():
    argv=owner.diagnostic_argv(__import__('pathlib').Path('/o'),123.0)
    assert argv[-2:]==["--deadline","123.0"]
    assert "diagnostic_run.py" in argv[1]
    assert owner.budget(10)=={"started":10,"work":280,"owned":300,"outer":310}
