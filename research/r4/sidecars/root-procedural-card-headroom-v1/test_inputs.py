"""Immutable package qualification, not a score-filtered panel."""
from pathlib import Path

def test_all_composed_blocks_pairing_source_truth_and_control_prefix():
    assert Path(__file__).with_name('inputs').exists(),'48-slot immutable native input builder not completed'
    import ph_study as s
    from collections import Counter
    originals={r['id']:r for r in s.read(s.CT/'inputs/FREE_PLAN.json') if r['panel']=='composition'}
    rows=s.read(s.ROOT/'inputs/FREE_PLAN.json');assert len(rows)==48 and len(originals)==24
    assert Counter(r['source_coordinate_id'] for r in rows)==Counter({k:2 for k in originals})
    changes={'id','namespace','seed','source_coordinate_id','card_arm','source_exposure'}
    oldprefix=s.read(s.CT/'inputs/PROMPTS_ACCURATE.json');prefix=s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')
    for row in rows:
        old=originals[row['source_coordinate_id']]
        assert {k:v for k,v in row.items() if k not in changes}=={k:v for k,v in old.items() if k not in changes}
        if row['card_arm']=='U':assert prefix[row['id']]==oldprefix[old['id']]
    for key in originals:
        pair=[r for r in rows if r['source_coordinate_id']==key]
        assert {r['card_arm'] for r in pair}=={'U','P'} and len({r['seed'] for r in pair})==1
    assert len({r['seed'] for r in rows})==24
    assert Counter(p['first_arm'] for p in s.read(s.ROOT/'inputs/PAIRS.json'))=={'U':12,'P':12}
    for name in ('PUBLIC.json','HOST_GOLD.json','GROUPS.json','NATIVE_TEMPLATE.json'):
        assert s.read(s.ROOT/'inputs'/name)==s.read(s.CT/'inputs'/name)
    native=s.read(s.ROOT/'CPU_INPUT_NATIVE.json');assert native['card_tokens']<=250 and len(native['rows'])==48
    assert all(x['original_files_equal'] and x['private_gold_invariant'] and x['prefix_tokens']+2048<=8192 for x in native['rows'])
    baseline=s.read(s.ROOT/'inputs/BASELINES.json');assert baseline['per_arm']==24 and baseline['zero_correct']==4
    plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');assert (plan['planned_full'],plan['first_action'])==(48,[])
    assert (plan['work_seconds'],plan['owned_seconds'],plan['outer_seconds'])==(2550,2670,2700)
