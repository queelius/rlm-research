"""Seal one successful cache proof; never launches a fixture or scientific job."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import isolation_short as owned
from copy_image import write,sha,OLD,ID,CAP

def main():
    root=owned.ROOT;q=root/'fixture-03'
    read=lambda p:json.loads(p.read_text())
    result=read(q/'RESULT.json');comparison=read(q/'COMPARISON.json');timing=read(q/'TIMING.json')
    assert result['provider_calls']==3 and result['gpu_calls']==0 and comparison['all_equal']
    assert not (q/'FAILURE.json').exists()
    commands=read(q/'SETUP_COMMANDS.json');offline=[r for r in commands if 'offline_result' in r];assert len(offline)==1
    test=subprocess.run(['/project/alex_phd/envs/rlm/bin/python','-m','unittest','test_isolation','-v'],cwd=root,
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=30)
    write(root/'TESTS.json',{'returncode':test.returncode,'stdout':test.stdout,'stderr':test.stderr});assert test.returncode==0
    argv,env=owned.command(['ps','-a','--format','json']);inventory=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=30)
    write(root/'CONTAINER_INVENTORY.json',{'argv':argv,'returncode':inventory.returncode,'stdout':inventory.stdout,'stderr':inventory.stderr})
    assert inventory.returncode==0 and read(root/'PRIVATE_INSPECT.json')['returncode']==0
    containers=json.loads(inventory.stdout);assert containers==[]
    usage=subprocess.run(['du','-sb',str(owned.STORE)],capture_output=True,text=True,check=True,timeout=30)
    size=int(usage.stdout.split()[0]);assert size<CAP
    copy=read(root/'COPY_MANIFEST.json');past=read(OLD/'fixture-03/TIMING.json')
    report={'image_id':ID,'copy_seconds':copy['copy_seconds'],'copy_and_hash_seconds':copy['copy_and_hash_seconds'],
        'fixture_seconds':timing['ended_epoch']-timing['started_epoch'],'prior_ceph_fixture_seconds':past['ended_epoch']-past['started_epoch'],
        'setup_elapsed_seconds':offline[0]['setup_elapsed'],'store_apparent_bytes_after_cleanup':size,'sampled_during_fixture_bytes':2063430100,
        'all_equal_native_requests':comparison,'owned_containers_remaining':0,'no_general_speedup_claim':True,'completed_epoch':time.time()}
    write(root/'RESULT.json',report)
    original=read(OLD/'CPU_READY.json');closure=dict(original['source_and_artifact_sha256'])
    base=read(root.parent/'root-only-credit-v1/SPEC.json');closure.update(base['source_file_sha256'])
    paths=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [OLD/'CPU_READY.json',OLD/'IMAGE_LAYER_MANIFEST.json',root.parent/'root-only-credit-v1/SPEC.json',root.parent/'rootless-runtime-feasibility-v1/bin/crun-isolated']
    for name in ('podman','crun','conmon'):paths.append(owned.original.STAGED/'usr/bin'/name)
    closure.update({str(p):sha(p) for p in paths})
    # Authenticate inherited source/artifacts once; never hash model weight tensors here.
    for path,digest in closure.items():assert sha(Path(path))==digest,path
    ready={'status':'CPU_QUALIFIED_FUTURE_ONLY','image_id':ID,'oci_manifest_digest':original['oci_manifest_digest'],
        'private_store':str(owned.STORE),'private_wrapper':str(root/'bin/docker'),'runtime_root':str(root),'owner_uid':os.getuid(),
        'cpu_affinity':[34,35],'allocation_cpu_affinity':[32,33,34,35,96,97,98,99],'allocation_memory_mib':65536,'proof_cap_bytes':CAP,
        'source_cache':str(OLD),'ephemeral':True,'resume':'Missing store invalidates readiness; no automatic recopy/retry/fallback.',
        'native_fixture_attempts':1,'fixture_compatibility_slot_name':'fixture-03 inherited offline-canary branch, not three new attempts',
        'gpu_calls':0,'real_model_calls':0,'source_and_artifact_sha256':closure,'metrics':report,'sealed_epoch':time.time(),
        'future_adoption':'Main may symmetrically bind exact new wrapper/store/image in a new study; accepted/live sources unchanged.'}
    write(root/'CPU_READY.json',ready);print(json.dumps({'ready':str(root/'CPU_READY.json'),'sha256':sha(root/'CPU_READY.json'),'metrics':report}),flush=True)

if __name__=='__main__':main()
