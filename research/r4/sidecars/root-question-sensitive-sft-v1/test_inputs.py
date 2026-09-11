"""Catches allocation leakage, resampling and public oracle injection."""
from pathlib import Path
from collections import Counter
import pytest

def test_corpus_admission_rejects_bad_current_action_mask(tmp_path,monkeypatch):
    import qs_study as s
    import qs_protocol as p
    row=s.read(s.ROOT/'inputs/TRAIN_PLAN.json')[0];directory=tmp_path/'capture'/row['id'];physical=directory/'physical/0002.json'
    turns={kind:p.row(kind,[1,2],[3,151645],kind) for kind in ('first_producer','corrective','terminal')}
    turns['corrective']['loss_mask'][0]=1
    s.write(physical,dict(origin='actual c32',physical_request_attempt=True))
    s.write(directory/'TEACHER.json',dict(episode_id=row['id'],coordinate=row,prefix_ids_verified=True,actual_child_records=[str(physical)],masked_history_turns=[],turns=turns))
    monkeypatch.setattr(s,'ATTEMPT',tmp_path)
    with pytest.raises(ValueError):s.corpus(1)

def test_frozen20_contexts72_training160_readout_and_disjoint320():
    assert (Path(__file__).parent/'inputs/PROVENANCE.json').exists(),'exact once-only allocation absent'
    import qs_study as s
    groups=s.read(s.ROOT/'inputs/GROUPS.json');train=s.read(s.ROOT/'inputs/TRAIN_PLAN.json');free=s.read(s.ROOT/'inputs/FREE_PLAN.json');dev=s.read(s.ROOT/'inputs/DEV_PLAN.json')
    assert Counter(g['split'] for g in groups)=={'train':8,'dev':4,'protected':8}
    selected=[x for g in groups for x in g['group_ids']];assert len(selected)==len(set(selected))==320
    proof=s.read(s.ROOT/'inputs/PROVENANCE.json');assert not set(selected)&set(proof['current_excluded_group_ids'])
    assert len(train)==72 and len(free)==72 and len(dev)==8
    assert {r['slot'] for r in dev}=={'M1','M2'}
    assert all(r['width']==16 and not r['metadata_error'] for r in train)
    plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');assert len(plan['full'])==160 and all(x['reward'] is None for x in plan['full'])
    proof=s.read(s.ROOT/'CPU_INPUT_NATIVE.json');assert all(x['gold_independent'] and x['exact_four_files'] for x in proof['rows'])
    assert len(proof['rows'])==180
