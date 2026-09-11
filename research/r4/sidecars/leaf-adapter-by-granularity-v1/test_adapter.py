def test_plan_pairs_same_native_input_and_only_changes_model():
    import prepare as prep
    plan,bodies=prep.build()
    assert len(plan)==152 and len({r['id'] for r in plan})==152
    cells={}
    for row in plan:
        k=(row['context_id'],row['repeat'],row['arm'],row['batch'])
        cells.setdefault(k,{})[row['model_policy']]=row
    assert len(cells)==76
    for cell in cells.values():
        assert set(cell)=={'base','c32'}
        a=dict(bodies[cell['base']['id']]);b=dict(bodies[cell['c32']['id']])
        assert a.pop('model')!=b.pop('model')
        assert a==b
        assert a['sampling_params']['seed'] in (986902701,986902702)

def test_summary_keeps_model_and_width_cells_separate():
    import bg_collect as c
    rows=[]
    for model in ('base','c32'):
        for arm in ('W','S'):
            rows.append(dict(coordinate=dict(context_id='scale-state-03-256',repeat=0,model_policy=model,arm=arm,n=1),
                             score=dict(strict_correct=1 if model=='base' else 0,available=True,complete_map=True,
                                        labels={'x':'numeric value' if model=='base' else 'entity'},canonical_id_matches=1)))
    out=c.summarize(rows,{'scale-state-03-256':{'labels':{'x':'numeric value'}}},
                    {'scale-state-03-256':{'records':[{'id':'x','weight':2}]}})
    assert len(out)==4
    assert {r['model_policy'] for r in out}=={'base','c32'}
    assert all(r['strict_correct']==int(r['model_policy']=='base') for r in out)
