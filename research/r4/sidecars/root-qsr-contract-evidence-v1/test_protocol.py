import json
from collections import defaultdict
import pytest

def test_exact_source_and_matched_twenty_four():
    import protocol as p
    import study as s
    value=p.build(); original=s.read(s.QSR/'inputs/PUBLIC.json')[:2]
    assert value['PUBLIC.json']==original
    rows=value['PLAN.json'];assert len(rows)==24 and len({r['id'] for r in rows})==24
    blocks=defaultdict(list)
    for row in rows:blocks[row['task_name']].append(row)
    assert len(blocks)==6
    for entries in blocks.values():
        assert len({r['seed'] for r in entries})==1
        assert {(r['role'],r['evidence']) for r in entries}=={('native','raw'),('native','map'),('compact','raw'),('compact','map')}
    old=s.read(s.QSR/'inputs/TASKS.json')
    for key,q in value['QUERIES.json'].items():
        assert q['original']==old[key]['question']
        if q['query']['scope']=='all':
            assert q['question'].startswith('Across all records, regardless of which of u0, u1, u2, or u3 owns the record,')
            assert q['question'].split(', a record qualifies',1)[1]==q['original'].split(', a record qualifies',1)[1]
        else:assert q['question']==q['original']

def test_wrong_labels_preserved_but_structural_failures_gate():
    import protocol as p
    assert p.map_state('{"qabc":"entity"}', ['qabc'])['labels']=={'qabc':'entity'}
    for raw in ('{}','{"qabc":"entity","qabc":"entity"}','{"qabc":"bogus"}','{"qabc":"entity","extra":"entity"}'):
        assert p.map_state(raw,['qabc'])['available'] is False

def test_strict_native_score_no_prose_repair():
    import protocol as p
    assert p.score('Answer: 3',3,True)['reward']==1
    assert p.score('The answer is 3. Answer: 3',3,True)['reward']==0
    assert p.score(None,3,False)['reward'] is None

def test_real_operator_not_copied_target():
    import protocol as p
    records=[dict(id='qa',user='u0',weight=4),dict(id='qb',user='u1',weight=7),dict(id='qc',user='u0',weight=2)]
    labels=dict(qa='entity',qb='entity',qc='entity')
    q=dict(users=['u0','u1'],target='entity')
    assert [p.answer(records,labels,{**q,'operator':op}) for op in ('count','distinct','weight')]==[3,2,13]
