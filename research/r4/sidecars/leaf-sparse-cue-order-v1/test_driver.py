from pathlib import Path

def test_owned_work_and_collection_caps_do_not_reset():
    import owned
    assert owned.ROOT==Path(__file__).resolve().parent
    assert owned.work_deadline(10)==790
    assert owned.collection_command_cap(10,20)==630
    assert owned.collection_command_cap(10,780)==10

def test_ordered_wire_hook_is_not_canonical_hash_only(tmp_path):
    import asyncio
    import httpx
    import driver
    s=driver.s;d=s.build_design(s.build_data());row=d['plan'][0];body=s.make_request(d,row)
    spec={'requests':{row['id']:body},'request_sha256':{row['id']:s.digest(body)}}
    asyncio.run(driver.wire_hook(spec,tmp_path)(httpx.Request('POST','http://fixture/v1/chat/completions',json=body)))
    assert s.read(tmp_path/'wire'/f"{row['id']}.json")['body_utf8']==s.serialize(body)
