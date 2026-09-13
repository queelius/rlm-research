"""Catch reused stages, changed history/normalization, or stale owner/metric binding."""
from pathlib import Path


def test_fresh_twelve_stage_inventory():
    assert (Path(__file__).parent/'study.py').exists(), 'fresh study not implemented'
    import study as s
    p=s.read(s.INPUTS);old=s.read(s.PRIOR/'PUBLIC_INPUTS.json')
    assert len(p['tasks'])==12 and len(p['calls'])==48
    assert not {t['root_id'] for t in p['tasks']}&{t['root_id'] for t in old['tasks']}
    assert [(t['history_depth'],t['width'],t['selected_stage']) for t in p['tasks']]==[(1,6,0),(1,6,1),(1,12,2),(1,12,0),(1,20,1),(1,20,2),(3,6,0),(3,6,1),(3,6,2),(3,12,0),(3,12,1),(3,12,2)]
    for task in p['tasks']:
        raw=task['raw_public_view'];rows=raw['stage']['tables']
        assert len(rows['implementations'])==task['width']
        assert len(rows['changes'])==task['width']*task['history_depth']
        assert task['normalized_prompt']==s.normalize.render(task['raw_prompt'])
        assert [r['implementation_id'] for r in rows['implementations']]==[r['implementation_id'] for r in task['normalized_public_view']['stage']['effective_candidates']]
        calls=[c for c in p['calls'] if c['root_id']==task['root_id']]
        assert len(calls)==4
        for repeat in (0,1):
            pair=[c for c in calls if c['repeat']==repeat]
            assert len({c['seed'] for c in pair})==1 and {c['arm'] for c in pair}=={'raw','normalized'}
    assert max(len(r['token_ids'])+384 for r in p['requests'].values())<=8192


def test_actual_new_pair_http_and_owner(tmp_path,monkeypatch):
    import study as s
    source=(s.PRIOR/'test_normalize.py').read_text()
    assert source.count('partial["unknown"]==34')==1
    source=source.replace('partial["unknown"]==34','partial["unknown"]==46')
    scope={'__file__':str(s.PRIOR/'test_normalize.py')}
    exec(compile(source,str(s.PRIOR/'test_normalize.py'),'exec'),scope)
    with s.aliases({'normalize':s.normalize},s.ROOT):
        scope['test_actual_frozen_raw_normalized_pair_http_and_unordered_metric'](tmp_path,monkeypatch)
