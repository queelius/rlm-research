"""Independent fixtures catch future/private leakage, unequal files and broken pairing."""
import importlib
import json
from pathlib import Path
import pytest

def api():
    assert (Path(__file__).parent/'protocol.py').exists(),'missing pre-cut export/protocol'
    return importlib.import_module('protocol')

def fixture():
    def node(parent,role,content,token,tools=None):
        return dict(parent=parent,message=dict(role=role,content=content,tool_calls=tools),token_ids=[token])
    nodes=[node(None,'system','SYSTEM',1),node(0,'user','GOAL',2),
           node(1,'assistant',None,3,[dict(name='ipython',arguments='{"code":"producer"}',id='call0')]),
           node(None,'system','PRIVATE CHILD SECRET',40),node(3,'assistant','PRIVATE CHILD ANSWER',41),
           node(2,'tool','{"q1":"human being","q2":"entity"}\n',4),
           node(5,'assistant','FUTURE CORRECTIVE CODE',5),node(6,'tool','FUTURE SCALAR',6),node(7,'assistant','FUTURE FINAL',7)]
    return dict(nodes=nodes,calls=[dict(node=2,model='root'),dict(node=4,model='child'),dict(node=6,model='root'),dict(node=8,model='root')])

def test_cut_keeps_only_actual_root_visible_prefix_not_private_or_future():
    p=api();value=p.cut(fixture(),'root',1,[1,2,3,4])
    assert [m['role'] for m in value['messages']]==['system','user','assistant','tool']
    assert value['node_indices']==[0,1,2,5]
    assert 'PRIVATE' not in json.dumps(value) and 'FUTURE' not in json.dumps(value)
    with pytest.raises(ValueError,match='prefix'):p.cut(fixture(),'root',1,[1,2,999])

def test_native_root_omits_parent_without_changing_cut():
    trace=fixture();trace['nodes'][0].pop('parent')
    assert api().cut(trace,'root',1,[1,2,3,4])['node_indices']==[0,1,2,5]

def test_generation_header_belongs_to_next_node_but_not_future_completion():
    trace=fixture();trace['nodes'][6]['token_ids']=[151644,77091,198,5]
    expected=[1,2,3,4,151644,77091,198]
    assert api().cut(trace,'root',1,expected)['prefix_token_ids']==expected

def test_package_preserves_wrong_actual_labels_and_rejects_missing_coverage():
    p=api();context=dict(records=[dict(id='q1',user='u0',text='Question1'),dict(id='q2',user='u1',text='Question2')])
    messages=p.cut(fixture(),'root',1,[1,2,3,4])['messages']
    files=p.package(context,'state0',messages,['u0'],'human being')
    assert json.loads(files['state/map-01.json'])=={'q1':'human being','q2':'entity'}
    assert json.loads(files['state/metadata.json'])['batch_coverage_ids']==[['q1','q2']]
    assert 'scalar' not in json.dumps(files).lower() and 'FUTURE' not in json.dumps(files)
    messages[-1]['content']='{"q1":"human being"}'
    with pytest.raises(ValueError,match='coverage'):p.package(context,'state0',messages,['u0'],'human being')

def test_three_prompts_reference_same_files_without_mutating_package():
    p=api();files={'state/history.json':'HISTORY_MARKER','state/metadata.json':'META_MARKER','state/map-01.json':'MAP_MARKER'}
    saved=dict(files);prompts={arm:p.prompt('COMMON GOAL',files,arm) for arm in ('Q','A','M')}
    assert files==saved
    assert all('state/history.json' in v and 'state/map-01.json' in v for v in prompts.values())
    assert 'HISTORY_MARKER' in prompts['Q'] and 'HISTORY_MARKER' not in prompts['A']+prompts['M']
    assert 'META_MARKER' in prompts['M'] and 'META_MARKER' not in prompts['A']

def test_all_sources_paired_once_per_arm_without_outcome_selection():
    p=api();states=[dict(source_id=f'state{i}',context_id=f'ctx{i//4}',native_context_id=i//4,family='union',users=['u0','u2'],width=4) for i in range(16)]
    rows=p.plan(states)
    assert len(rows)==48 and len({r['id'] for r in rows})==48
    for state in states:
        pair=[r for r in rows if r['source_id']==state['source_id']]
        assert {r['representation'] for r in pair}=={'Q','A','M'}
        assert len({r['seed'] for r in pair})==1
    assert len({r['seed'] for r in rows})==16
