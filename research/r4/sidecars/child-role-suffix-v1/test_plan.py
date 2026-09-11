from pathlib import Path


def test_sixteen_coordinates_pair_identical_root_inputs_and_balance_order():
    assert (Path(__file__).parent/'experiment.py').exists(), 'prospective plan not implemented'
    import experiment as e
    tasks=e.make_tasks()
    plan=e.build_plan(tasks)
    assert len(tasks)==4 and len(plan)==16 and len({r['id'] for r in plan})==16
    assert {r['seed'] for r in plan}=={893350289,62794825}
    assert [r['arm'] for r in plan].count('control')==8
    assert [plan[i]['arm'] for i in range(0,16,2)].count('control')==4
    for i in range(0,16,2):
        a,b=plan[i:i+2]
        assert a['arm']!=b['arm']
        assert all(a[k]==b[k] for k in ('pair_id','seed','task_name','context_sha256','task_hash'))
        assert e.with_prompt(tasks[a['task_name']],a['arm']).data.prompt==e.with_prompt(tasks[b['task_name']],b['arm']).data.prompt
