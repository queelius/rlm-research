from pathlib import Path
def test_owned_caps_do_not_reset():
    import owned
    assert owned.ROOT==Path(__file__).resolve().parent
    assert owned.work_deadline(10)==760
    assert owned.collection_command_cap(10,20)==630
    assert owned.collection_command_cap(10,750)==10

def test_ordered_wire_capture(tmp_path):
    import asyncio,httpx,driver
    s=driver.s;d=s.build_design(s.build_data());r=d['plan'][0];b=s.make_request(d,r)
    spec={'requests':{r['id']:b},'request_sha256':{r['id']:s.digest(b)}}
    asyncio.run(driver.wire_hook(spec,tmp_path)(httpx.Request('POST','http://fixture/v1/chat/completions',json=b)))
    assert s.read(tmp_path/'wire'/f"{r['id']}.json")['body_utf8']==s.serialize(b)
