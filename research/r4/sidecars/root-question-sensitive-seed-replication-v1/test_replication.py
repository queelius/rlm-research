import study as s


def test_fresh_paired_plan_changes_only_sampling_identity():
    old=s.base.read(s.base.ROOT/'inputs/FREE_PLAN.json')
    new=s.build_plan(old)
    assert len(new)==72 and len({r['id'] for r in new})==72
    assert not {r['id'] for r in new}&{r['id'] for r in old}
    assert not {r['seed'] for r in new}&{r['seed'] for r in old}
    for a,b in zip(old,new):
        assert {k:v for k,v in a.items() if k not in s.CHANGED}=={k:v for k,v in b.items() if k not in s.CHANGED}


def test_both_exact_frozen_policies_keep_child():
    a,b=s.binding('unchanged'),s.binding('sft6')
    assert a['models'][a['fixed_child']]==b['models'][b['fixed_child']]
    assert a['models'][a['role_map']['root']]['adapter_sha256']!=b['models'][b['role_map']['root']]['adapter_sha256']
    assert b['models'][b['role_map']['root']]['adapter_sha256']=='4d8287537a9ff3d8e33bc0314f64315dee06e71b801257b389dab8b667e27aca'
