"""One bounded immutable-chain copy, no live metadata or shared writer."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import isolation_short as owned

OLD=owned.ROOT.parent/'runtime-preinstalled-image-v1/attempt-002'
MANIFEST=OLD/'IMAGE_LAYER_MANIFEST.json'
LIVE=Path('/project/alex_phd/research-cache/runtime-images/rpi-v2.kCaOH4/root')
ID='8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c'
CAP=12*1024**3
def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(value,f,indent=2)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    os.sched_setaffinity(0,{34,35});start=time.time();deadline=start+600
    assert sha(MANIFEST)=='84c0481f9779aafb0d736a75189f793322b28ad29e9a438be0b03e447764e721'
    frozen=json.loads(MANIFEST.read_text());image=frozen['image'];layers=frozen['immutable_layer_chain'];assert image['id']==ID and len(layers)==6
    for name in ('root','runroot','runtime','config','tmp','verifiers-cache'):(owned.STORE/name).mkdir(mode=0o700)
    sources=[LIVE/'vfs-images'/ID]+[LIVE/'vfs/dir'/x['id'] for x in layers]+[LIVE/'vfs-layers'/(x['id']+'.tar-split.gz') for x in layers]
    listing=[];total=0
    for source in sources:
        paths=source.rglob('*') if source.is_dir() else [source]
        for p in paths:
            if p.is_symlink():listing.append((p,'symlink',os.readlink(p),0))
            elif p.is_file():total+=p.stat().st_size;listing.append((p,'file',None,p.stat().st_size))
    # Reserve another full top-layer copy, plus2GiB for the one runtime/cache fixture.
    if total*2+2*1024**3>CAP:raise ValueError('copy plus one runtime exceeds conservative12GiB envelope')
    write(owned.ROOT/'COPY_PLAN.json',{'started_epoch':start,'copy_deadline':deadline,'store':str(owned.STORE),'source_root':str(LIVE),
        'owner_uid':os.getuid(),'image_id':ID,'layer_ids':[x['id'] for x in layers],'paths':list(map(str,sources)),
        'apparent_source_bytes':total,'reserved_estimate_bytes':total*2+2*1024**3,'cap_bytes':CAP,
        'no_live_database_read_or_copy':True,'frozen_metadata_sha256':sha(MANIFEST)})
    copied_at=time.time()
    for source in sources:
        target=owned.STORE/'root'/source.relative_to(LIVE);target.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['cp','-a','--reflink=never',str(source),str(target)],check=True,timeout=max(.1,deadline-time.time()))
    copy_seconds=time.time()-copied_at;entries=[]
    for p,kind,link,size in listing:
        if time.time()>deadline:raise TimeoutError('aggregate immutable-copy envelope')
        target=owned.STORE/'root'/p.relative_to(LIVE)
        if kind=='file':digest=sha(p);assert sha(target)==digest
        else:digest=None;assert os.readlink(target)==link
        entries.append({'source':str(p),'target':str(target),'kind':kind,'bytes':size,'sha256':digest,'symlink_target':link})
    write(owned.STORE/'root/vfs-images/images.json',[image])
    write(owned.STORE/'root/vfs-layers/layers.json',list(reversed(layers)))
    write(owned.ROOT/'COPY_MANIFEST.json',{'entries':entries,'source_bytes':total,'copy_seconds':copy_seconds,'copy_and_hash_seconds':time.time()-start})
    argv,env=owned.command(['image','inspect',ID]);result=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=60)
    write(owned.ROOT/'PRIVATE_INSPECT.json',{'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    assert result.returncode==0,result.stderr
    assert json.loads(result.stdout)[0]['Id'].removeprefix('sha256:')==ID
    write(owned.ROOT/'IMAGE.json',{'image_id':ID})
    print(json.dumps({'image':ID,'files':len(entries),'source_bytes':total,'copy_seconds':copy_seconds,'seconds':time.time()-start}),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException as error:
        write(owned.ROOT/'COPY_FAILURE.json',{'type':type(error).__name__,'message':str(error),'ended_epoch':time.time(),'retry':False});raise
