"""Saved real native fixture: no live fixture/model execution or outcome scoring."""
import json
import pytest
import study as s
from capture import scalar_from_prefix

def test_failed_native_tool_trajectory_is_null_but_completed_empty_is_observed():
    import readout
    assert hasattr(readout,'native_unavailable'),'native endpoint availability guard missing'
    returned={'status':'returned'}
    assert readout.native_unavailable(returned,{'ok':False,'stop_condition':'error','root_reply':''})
    assert not readout.native_unavailable(returned,{'ok':True,'is_completed':True,'root_reply':''})
    assert not readout.native_unavailable(returned,{'ok':True,'is_completed':True,'root_reply':'Answer: 2'})
    assert readout.native_unavailable(None,{'root_reply':''})

def test_native_second_prefix_and_actual_scalar_not_dataset_replacement():
    q=s.PLAN/'qualification-002';raw=s.read(q/'canonical/EPISODE.json');physical=s.read(q/'CPU_PROVIDER_REQUESTS.json')
    st=s.stack();renderer=st.native.renderer();template=s.read(s.PLAN/'prepared-v2/NATIVE_TEMPLATE.json')
    nodes=raw['traces'][0]['nodes'];action=next(n for n in nodes if n.get('message',{}).get('role')=='assistant');tools=[n for n in nodes if n.get('message',{}).get('role')=='tool']
    messages=[nodes[0]['message'],nodes[1]['message'],action['message'],tools[0]['message']]
    ids=renderer.render(messages,tools=json.loads(template['tools_ordered_json']),add_generation_prompt=True).token_ids
    root=[r['body']['token_ids'] for r in physical if r['arm']=='canonical' and 'campaign-root' in r['body']['model']]
    assert len(root)==2 and ids==root[1]
    text=renderer._tokenizer.decode(ids,skip_special_tokens=False)
    assert scalar_from_prefix(text)==2
    with pytest.raises(ValueError):scalar_from_prefix('<tool_response>\n{"a":2}\n</tool_response>')
    with pytest.raises(ValueError):scalar_from_prefix('<tool_response>\nTraceback\n</tool_response>')

def test_real_collector_new_panel_and_source_metadata_not_old_fixture():
    from readout import compose
    collector,st=compose();recipe=s.read(s.ROOT/'RECIPE.json');prepared=s.ROOT/'prepared'
    assert collector.s.ROOT==s.ROOT and recipe['prepared']==str(prepared)
    plan=s.read(prepared/'EVAL_PLAN_FINAL.json');public=s.read(prepared/'PUBLIC.json')
    assert len(plan)==16 and len({r['id'] for r in plan})==16
    assert len({st.prior.context_window_id(c) for c in public})==4
    assert {st.prior.context_window_id(c) for c in public}=={98133000,98133001,98133002,98133003}
    assert len({r['seed'] for r in plan})==16
    for c in public:
        task=st.native.task(c,st.prior.prompt(c,'single_user'),0,'cpu-proof')
        assert task.data.dataset==s.ROOT.name
        assert task.data.source_split=='root-disjoint-helper-'+c['helper_partition']
        assert task.data.context_window_id==st.prior.context_window_id(c)
