import study as s

def test_metadata_shift_preserves_text_order_and_changes_every_weight_and_user():
    original=s.read(s.ORIGINAL/'inputs/PUBLIC.json')
    original=[x for x in original if x['split']=='protected']
    contexts,rows=s.transfer_inputs()
    assert len(contexts)==8 and len(rows)==72
    for old,new in zip(original,contexts):
        for a,b in zip(old['records'],new['records']):
            assert (a['id'],a['text'])==(b['id'],b['text'])
            assert b['user']=='u'+str(int(a['user'][1:])+4)
            assert 8<=b['weight']<=15 and a['weight']!=b['weight']
    for row in rows:
        assert set(row['users'])<={'u4','u5','u6','u7'}
        assert row['threshold'] in (None,13,25)
        assert not any(name in row['question'] for name in ('u0','u1','u2','u3'))
