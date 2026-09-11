from pathlib import Path

def test_nested_records_and_literal_truth():
    assert Path(__file__).with_name('prepare.py').exists(),'new label-blind scale allocator missing'
    import prepare as p
    pool=[dict(group_id=f'{i:064x}',question='question '+str(i),gold='human being' if i%2 else 'entity',source_path='CPU',source_line_1based=i+1) for i in range(1024)]
    out=p.build(pool);contexts=out['PUBLIC.json'];parents=out['PARENTS.json']
    assert len(contexts)==12 and len(parents)==4 and len(out['FREE_PLAN.json'])==24
    assert len({g for parent in parents for g in parent['group_ids']})==1024
    for parent in parents:
        cs=sorted([c for c in contexts if c['parent_id']==parent['id']],key=lambda c:c['size'])
        assert [c['size'] for c in cs]==[16,128,256]
        assert cs[0]['records']==cs[1]['records'][:16]==cs[2]['records'][:16]
        assert cs[1]['records']==cs[2]['records'][:128]
    changed=p.build([{**r,'gold':'numeric value'} for r in pool])
    for key in ('PUBLIC.json','PARENTS.json','GROUPS.json','FREE_PLAN.json','EVALUATION_PLAN.json'):
        assert out[key]==changed[key],'labels changed public selection or task'
    import ss_study as s
    records=[dict(id='a',user='u0',weight=5),dict(id='b',user='u1',weight=2),dict(id='c',user='u2',weight=7)]
    labels={'a':'human being','b':'entity','c':'human being'}
    assert s.answer(records,labels,dict(operator='count',target='human being'))==2
    assert s.answer(records,labels,dict(operator='weight_sum',target='human being'))==12

def test_exact_single_policy_collector_cli():
    assert Path(__file__).with_name('ss_owner.py').exists(),'new bounded scale owner missing'
    import ss_owner as o
    import ss_collect as c
    stage=Path('/CPU/service-sft24');dest=Path('/CPU/sft24/free')
    argv=o.collector_argv(stage,dest,123.);args=c.implementation().parse_args(argv[2:])
    assert args.mode=='free' and args.plan=='FREE_PLAN.json' and args.start==0 and args.stop==24
    assert args.output==dest and args.binding==stage/'BINDING.json'
