import json
def test_protocol_preserves_input_and_freezes_six_conditions():
    import protocol_v2 as p
    rows=p.plan();assert len(rows)==48 and len({r['id'] for r in rows})==48
    c=p.contexts()[0]
    for rel in ('wrong','alien','aligned'):
        sub={r['arm']:r for r in rows if r['context_index']==0}
        a=p.request(c,sub[rel+'_tag_first']);b=p.request(c,sub[rel+'_labels_only'])
        assert a['seed']==b['seed']==983626101
        assert p.visible_records(c,rel+'_tag_first')==p.visible_records(c,rel+'_labels_only')
        assert a['messages'][1]['content'].split('Input records ')[1]==b['messages'][1]['content'].split('Input records ')[1]
        assert b['structured_outputs']['json']['items']['enum']==list(p.LABELS)

def test_host_join_is_whole_contract_positional_and_has_no_gold():
    import protocol_v2 as p,scoring_v2 as sc
    c=p.contexts()[0];labels=[r['gold_label'] for r in c['records']]
    good=sc.score({'content':json.dumps(labels)},c,'wrong_labels_only')
    assert good['strict_correct']==48 and good['contract_valid']
    assert good['tag_position_matches'] is None
    assert sc.host_join(['neutral']*48,p.requested_tags(c))==list(zip(p.requested_tags(c),['neutral']*48))
    for bad in (labels[:-1],labels+['neutral'],[{}]+labels[1:],['alien']+labels[1:]):
        x=sc.score({'content':json.dumps(bad)},c,'wrong_labels_only')
        assert x['available'] and x['strict_correct']==0 and not x['contract_valid']

def test_tag_first_still_checks_order_and_exact_tags():
    import protocol_v2 as p,scoring_v2 as sc
    c=p.contexts()[0];tags=p.requested_tags(c)
    v=[dict(tag=t,label=r['gold_label']) for t,r in zip(tags,c['records'])]
    assert sc.score({'content':json.dumps(v)},c,'wrong_tag_first')['strict_correct']==48
    v[0]=dict(reversed(list(v[0].items())))
    assert sc.score({'content':json.dumps(v)},c,'wrong_tag_first')['strict_correct']==0
