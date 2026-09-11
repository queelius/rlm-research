import asyncio
import time

import pytest


def test_actual_dispatch_keeps_eight_group_and_twenty_four_readout_slots():
    from collect import dispatch
    async def run(size):
        seen=[]
        async def one(row):seen.append(row['id'])
        assert await dispatch([{'id':i} for i in range(size)],one,time.time()+5) is None
        assert sorted(seen)==list(range(size))
    asyncio.run(run(8));asyncio.run(run(24))


def test_all_candidate_prompts_and_fresh_seeds_are_frozen():
    import study as s
    plans=s.build_plans(s.data()[0]);rows=[r for groups in plans['windows'].values() for g in groups for r in g]
    assert len(rows)==128 and len({r['id'] for r in rows})==128
    assert len({r['seed'] for r in rows+plans['readout']})==152
    assert len(plans['readout'])==24
    for groups in plans['windows'].values():
        assert [len(g) for g in groups]==[8]*4
        assert len({g[0]['task_name'] for g in groups})==4
        assert {g[0]['family'] for g in groups[:2]}=={'global','single_user'}


def test_consumed_prefix_is_neither_arbitrary_subset_nor_next_policy():
    from export import validate_consumed
    import study as s
    plans=s.build_plans(s.data()[0]);groups=plans['windows']['1']
    generation={'candidate_window':1,'coordinate_plan_sha256':s.digest(sum(groups,[])),'generation_id':'g'}
    manifests=[{'generation':generation,'planned':8,'recorded':8,'complete':True,'integrity_failures':[],
                'coordinate_plan_sha256':s.digest(g),'training_group_episodes':8} for g in groups[:2]]
    rows=sum([[{'episode_id':r['id'],'coordinate':r,'split':'training','generation_id':'g','qualification_only':False} for r in g] for g in groups[:2]],[])
    assert validate_consumed(generation,manifests,rows,groups)==[True,True]
    with pytest.raises(ValueError):validate_consumed(generation,manifests,rows[:-1],groups)
    bad=[dict(m) for m in manifests];bad[1]['generation']={**generation,'generation_id':'stale'}
    with pytest.raises(ValueError):validate_consumed(generation,bad,rows,groups)
    with pytest.raises(ValueError):validate_consumed(generation,manifests[::-1],rows,groups)


def test_real_mixed_selector_keeps_nulls_out_and_rejects_fixture_likelihood():
    import copy
    import export as e
    rows=[]
    for index,reward in enumerate((1,0,None)):
        rows.append(dict(episode_id=str(index),task_id='one-prompt',split='training',sample_seed=index,
            temperature=.5,trace_trainable=reward is not None,reward=reward,generation_id='fresh',qualification_only=False,
            turns=[dict(input_ids=[1,2],labels=[-100,2],loss_mask=[0,1],prompt_length=1,old_logprobs=[-.5])]))
    before=copy.deepcopy(rows)
    group=e.impl.mixed_group(rows,{'generation_id':'fresh'},{},'synthetic-only')
    assert [r['episode_id'] for r in group['episodes']]==['0','1']
    assert [r['advantage'] for r in group['episodes']]==[1.,-1.] and rows==before
    assert e.impl.mixed_group(rows[:1],{'generation_id':'fresh'},{},'synthetic-only') is None
    rows[0]['qualification_only']=True
    with pytest.raises(ValueError,match='qualification'):e.impl.mixed_group(rows,{'generation_id':'fresh'},{},'synthetic-only')


def test_exact_native_fixture_root_masks_and_scientific_rejection():
    import native as n
    import study as s
    st=n.stack();directory=s.PRIOR/'qualification-typed-001';episode=s.read(directory/'EPISODE.json')
    roots,evidence=n.exact_turns(episode,directory,st.native.initial_binding(),qualification=True)
    assert len(roots)==2 and [r['role_depth'] for r in evidence]==[0,1,0]
    assert evidence[1]['typed_wire_grammar'] is True and not evidence[1]['credited']
    assert all(t['typed_wire_grammar'] is False and t['labels'][:t['prompt_length']]==[-100]*t['prompt_length'] for t in roots)
    with pytest.raises(ValueError,match='qualification'):n.exact_turns(episode,directory,st.native.initial_binding())
