import hashlib
import json
import ast
from pathlib import Path


def test_private_run_and_owned_caps_are_exact():
    import driver
    import owned
    assert driver.RUN_EDITS==[('96','144',3),('min(600,','min(900,',1)]
    assert owned.work_deadline(10)==1090
    assert owned.collection_command_cap(10,20)==930
    assert owned.collection_command_cap(10,1000)==90
    assert owned.ROOT==Path(__file__).resolve().parent


def test_ordered_wire_hook_matches_complete_bytes(tmp_path):
    import asyncio
    import httpx
    import driver
    s=driver.s;design=s.build_design(s.build_data());row=design['plan'][0];body=s.make_request(design,row)
    spec={'requests':{row['id']:body},'request_sha256':{row['id']:s.digest(body)}}
    async def check():
        await driver.wire_hook(spec,tmp_path)(httpx.Request('POST','http://fixture/v1/chat/completions',json=body))
    asyncio.run(check())
    actual=s.read(tmp_path/'wire'/f"{row['id']}.json")
    assert actual['body_utf8']==s.serialize(body) and actual['body_sha256']==hashlib.sha256(actual['body_utf8'].encode()).hexdigest()
