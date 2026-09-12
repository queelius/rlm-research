"""Same immutable screen, additive CPU-validator repair and fresh attempt only."""
import study as previous

ROOT=previous.ROOT
ATTEMPT=ROOT/'outputs/attempt-002'
READY=ROOT/'READY_V2.json'

def __getattr__(name):return getattr(previous,name)

def verify():
    previous.verify()
    value=previous.read(READY)
    assert value['identity']==previous.digest({k:v for k,v in value.items() if k!='identity'})
    for path,want in value['closure_sha256'].items():assert previous.sha(path)==want,path
    assert value['schedule_sha256']==previous.digest(previous.plan())
    return value
