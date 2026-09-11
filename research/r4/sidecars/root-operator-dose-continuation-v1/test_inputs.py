"""Selection is label-blind; old/new paired coordinates remain distinct and complete."""
import importlib.util
from pathlib import Path

def test_selection_does_not_depend_on_labels():
    path=Path(__file__).with_name('prepare.py');assert path.exists(),'input builder missing'
    spec=importlib.util.spec_from_file_location('dose_prepare_test',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    pool=[dict(group_id=f'{i:064x}',question=f'Question {i}',gold='human being') for i in range(100)]
    first=m.new_contexts(pool)
    second=m.new_contexts([{**r,'gold':'location'} for r in pool])
    assert first['PUBLIC.json']==second['PUBLIC.json'] and first['GROUPS.json']==second['GROUPS.json']
    assert first['FREE_PLAN.json']==second['FREE_PLAN.json']
    assert len(first['PUBLIC.json'])==4 and len(first['FREE_PLAN.json'])==24
    assert len({g for row in first['GROUPS.json'] for g in row['group_ids']})==64
    for c in first['PUBLIC.json']:
        rows=[r for r in first['FREE_PLAN.json'] if r['context_id']==c['id']]
        assert len(rows)==6 and sum(r['heldout_cell'] for r in rows)==3
