"""Authenticate one CPU fixture and fresh lifecycle-only source closure."""
import json
import os
from pathlib import Path
import subprocess
import time
import isolation_short as owned
from copy_image import sha, write, OLD, ID, CAP

def main():
    root = owned.ROOT
    q = root / 'fixture-03'
    read = lambda p: json.loads(p.read_text())
    result, comparison, timing = [read(q / name) for name in ('RESULT.json', 'COMPARISON.json', 'TIMING.json')]
    assert result['provider_calls'] == 3 and result['gpu_calls'] == 0 and comparison['all_equal']
    assert not (q / 'FAILURE.json').exists()
    commands = read(q / 'SETUP_COMMANDS.json')
    offline = [row for row in commands if 'offline_result' in row]
    assert len(offline) == 1
    # delta() consumes readiness hash only when actually invoked, after publication.
    tests = subprocess.run(['/project/alex_phd/envs/rlm/bin/python', '-m', 'unittest', 'test_isolation', 'test_study_wrapper', '-v'],
        cwd=root, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'}, capture_output=True, text=True, timeout=30)
    write(root / 'TESTS.json', dict(returncode=tests.returncode, stdout=tests.stdout, stderr=tests.stderr))
    assert tests.returncode == 0
    argv, env = owned.command(['ps', '-a', '--format', 'json'])
    inventory = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=30)
    write(root / 'CONTAINER_INVENTORY.json', dict(argv=argv, returncode=inventory.returncode, stdout=inventory.stdout, stderr=inventory.stderr))
    assert inventory.returncode == 0 and json.loads(inventory.stdout) == []
    usage = subprocess.run(['du', '-sb', str(owned.STORE)], capture_output=True, text=True, check=True, timeout=30)
    size = int(usage.stdout.split()[0])
    assert size < CAP
    copy = read(root / 'COPY_MANIFEST.json')
    report = dict(image_id=ID, copy_seconds=copy['copy_seconds'], copy_and_hash_seconds=copy['copy_and_hash_seconds'],
        fixture_seconds=timing['ended_epoch']-timing['started_epoch'], setup_elapsed_seconds=offline[0]['setup_elapsed'],
        store_apparent_bytes_after_cleanup=size, all_equal_native_requests=comparison, owned_containers_remaining=0,
        no_general_speedup_claim=True, completed_epoch=time.time())
    write(root / 'RESULT.json', report)
    original = read(OLD / 'CPU_READY.json')
    closure = dict(original['source_and_artifact_sha256'])
    closure.update(read(root.parent / 'root-only-credit-v1/SPEC.json')['source_file_sha256'])
    paths = [p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths.extend(root.parent / 'runtime-local-cache-v1' / name for name in ('copy_image.py', 'fixture.py'))
    paths.extend([OLD / 'CPU_READY.json', OLD / 'IMAGE_LAYER_MANIFEST.json', root.parent / 'rootless-runtime-feasibility-v1/bin/crun-isolated'])
    paths.extend(owned.original.STAGED / 'usr/bin' / name for name in ('podman','crun','conmon'))
    closure.update({str(p):sha(p) for p in paths})
    for path, digest in closure.items():
        assert sha(Path(path)) == digest, path
    ready = dict(status='CPU_QUALIFIED_FUTURE_ONLY', image_id=ID, oci_manifest_digest=original['oci_manifest_digest'],
        private_store=str(owned.STORE), private_wrapper=str(root/'bin/docker'), runtime_root=str(root),
        owner_uid=os.getuid(), node='an27', allocation='5780', cpu_affinity=[14,15], allocation_cpu_affinity=list(range(16)),
        allocation_memory_mib=65536, proof_cap_bytes=CAP, ephemeral=True, native_fixture_attempts=1,
        fixture_compatibility_slot_name='fixture-03 inherited offline-canary branch; exactly one current attempt',
        gpu_calls=0, real_model_calls=0, source_and_artifact_sha256=closure, metrics=report, sealed_epoch=time.time(),
        acceptance='MAIN must pin this CPU_READY plus study_wrapper and own the new parent; no launch authority granted',
        resume='Missing store invalidates readiness. No recopy/retry/fallback.')
    write(root / 'CPU_READY.json', ready)
    print(json.dumps(dict(ready=str(root/'CPU_READY.json'), sha256=sha(root/'CPU_READY.json'), metrics=report)), flush=True)

if __name__ == '__main__':
    main()
