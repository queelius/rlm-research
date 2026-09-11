import importlib.util
from collections import Counter
from pathlib import Path


def module(name):
    path=Path(__file__).with_name(name+'.py')
    assert path.exists(), name+' implementation missing'
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def test_plan_preserves_eight_blocks_and_balances_treatment_position():
    p=module('protocol')
    contexts=[dict(id='c'+str(i),stratum='s',helper_partition='train' if i<2 else 'validation') for i in range(4)]
    rows=p.plan_for(contexts)
    assert len(rows)==32 and len({r['id'] for r in rows})==32 and len({r['seed'] for r in rows})==8
    for block in {r['pair_id'] for r in rows}:
        selected=[r for r in rows if r['pair_id']==block]
        assert len({r['seed'] for r in selected})==1
        assert {(r['example'],r['inline']) for r in selected}=={(False,False),(False,True),(True,False),(True,True)}
    assert set(Counter((r['example'],r['inline'],r['treatment_order']) for r in rows).values())=={2}


def test_example_removal_preserves_query_and_inline_is_exact_file_bytes():
    p=module('protocol')
    base='records id, synthetic user metadata, and original question text. No source semantic labels are present.\n\nOptional API example (first four records only, NOT the final answer):\n```python\nSECRET_EXAMPLE\n```\n\nReturn only Answer: N\nQuestion: requested users'
    payload=b'{"q0001": "human being"}'
    for example in (False,True):
        for inline in (False,True):
            text=p.prompt(base,dict(example=example,inline=inline),payload)
            assert ('SECRET_EXAMPLE' in text)==example
            assert ('<supplied_labels_json>\n'+payload.decode()+'\n</supplied_labels_json>' in text)==inline
            assert 'Question: requested users' in text and 'labels.json' in text and 'child predictions' in text
            assert 'synthetic user metadata' not in text and 'count_labels' not in text


def test_native_final_requires_no_tools_and_no_decimal_repair():
    m=module('metrics')
    capture=dict(status='returned',native_response=dict(finish_reason='stop',message=dict(content='Answer: 2',tool_calls=[])))
    assert m.score(dict(root_reply='Answer: 2'),capture,2)['reward']==1
    capture['native_response']['message']['tool_calls']=[dict(name='ipython')]
    assert m.score(dict(root_reply='Answer: 2'),capture,2)['reward'] is None
    capture['native_response']['message']=dict(content='Answer: 2.0',tool_calls=[])
    assert m.score(dict(root_reply='Answer: 2.0'),capture,2)['reward']==0


def test_reused_acquisition_is_full_pipeline_cost_but_not_new_physical_cost():
    m=module('metrics')
    result=m.pipeline_cost(dict(calls=3,known={'input':10,'output':2},unknown={'input':0,'output':0}),dict(calls=1,known={'input':7,'output':4},unknown={'input':0,'output':0}))
    assert result['new_physical']['known']['input']==10
    assert result['standalone_full_pipeline']['known']=={'input':17,'output':6}
    assert result['standalone_full_pipeline']['calls']==4
