"""Terminate only the saved process identity left by our failed8B startup."""
import hashlib
import json
import os
from pathlib import Path
import signal
import time

ROOT=Path(__file__).resolve().parent
SERVICE=Path('/project/alex_phd/runs/rlm-research-r4/sidecars/b05-qwen3-8b-direct-oracle-v1/outputs/attempt-002/service')
RECEIPT=SERVICE/'OWNED_PROCESSES/1166392-1106281859.json'
PID=1166392

def identity(pid):
    path=Path('/proc')/str(pid)
    fields=(path/'stat').read_text().rsplit(')',1)[1].split()
    return dict(pid=pid,uid=path.stat().st_uid,ppid=int(fields[1]),pgid=os.getpgid(pid),start_ticks=int(fields[19]),state=fields[0])

if __name__=='__main__':
    expected=json.loads(RECEIPT.read_text())['process'];actual=identity(PID)
    assert all(actual[k]==expected[k] for k in ('pid','uid','pgid','start_ticks'))
    assert actual['pgid']==PID and actual['uid']==os.getuid()
    start=json.loads((SERVICE/'service/SERVER_START.json').read_text())
    assert start['pid']==PID and start['command'][-1]==str(SERVICE/'service/inference.json')
    child=identity(1166536)
    assert child['ppid']==PID and child['pgid']==PID and child['uid']==actual['uid']
    members=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:value=identity(int(p.name))
        except (FileNotFoundError,ProcessLookupError,PermissionError):continue
        if value['pgid']==PID:
            assert value['uid']==actual['uid'];members.append(value)
    record=dict(authority='MAIN',epoch=time.time(),signal='SIGTERM',external_flock=True,
        ownership_receipt=str(RECEIPT),ownership_sha256=hashlib.sha256(RECEIPT.read_bytes()).hexdigest(),
        group_leader=actual,members=members,files_removed=0,
        reason='New8B launcher spawned owned group, but inherited service claim rejected its launcher binding and release failed before scientific calls.')
    with (ROOT/'OWNED_SIGTERM.json').open('x') as stream:json.dump(record,stream,indent=2,sort_keys=True);stream.write('\n')
    os.killpg(PID,signal.SIGTERM)
    print(json.dumps(dict(signaled_owned_pgid=PID,members=[x['pid'] for x in members],files_removed=0)))
