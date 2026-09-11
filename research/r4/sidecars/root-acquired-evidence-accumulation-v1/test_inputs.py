"""Characterize immutable admission: all fixed large blocks, paired arms, no source changes."""
from collections import Counter
import ae_study as s

def test_all_large_blocks_source_fields_pairing_and_caps():
    originals={r['id']:r for r in s.read(s.SS/'inputs/FREE_PLAN.json') if r['records'] in (128,256)}
    rows=s.read(s.ROOT/'inputs/FREE_PLAN.json');assert len(rows)==32 and len(originals)==16
    assert Counter(r['source_coordinate_id'] for r in rows)==Counter({k:2 for k in originals})
    changes={'id','namespace','seed','source_coordinate_id','accumulation_arm','source_exposure','stratum'}
    for row in rows:
        old=originals[row['source_coordinate_id']]
        assert {k:v for k,v in row.items() if k not in changes}=={k:v for k,v in old.items() if k not in changes}
    for key in originals:
        pair=[r for r in rows if r['source_coordinate_id']==key]
        assert {r['accumulation_arm'] for r in pair}=={'B','C'} and len({r['seed'] for r in pair})==1
    assert len({r['seed'] for r in rows})==16
    assert Counter(p['first_arm'] for p in s.read(s.ROOT/'inputs/PAIRS.json'))=={'B':8,'C':8}
    public=s.read(s.ROOT/'inputs/PUBLIC.json');oldpublic={c['id']:c for c in s.read(s.SS/'inputs/PUBLIC.json')}
    assert all(c==oldpublic[c['id']] for c in public)
    assert len(public)==8 and len({c['parent_id'] for c in public})==4
    assert len({r['id'] for c in public for r in c['records']})==1024
    checks=s.read(s.ROOT/'CPU_INPUT_NATIVE.json')['rows'];assert len(checks)==32 and all(x['gold_independent'] and x['prefix_tokens']+2048<=8192 for x in checks)
    plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');assert (plan['planned_full'],plan['first_action'])==(32,[])
    assert (plan['work_seconds'],plan['owned_seconds'],plan['outer_seconds'])==(1650,1770,1800)
