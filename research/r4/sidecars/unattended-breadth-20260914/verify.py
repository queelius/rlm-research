"""Compact pilot/provenance receipt; never reads or exports private service files."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import time

ROOT=Path(__file__).resolve().parent
def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def save(name,value):
    with (ROOT/name).open('x') as stream: json.dump(value,stream,indent=2)

if __name__=='__main__':
    command=['/project/alex_phd/envs/prime-rl-5990b1b/bin/python','-m','pytest',
        str(ROOT/'test_runner.py'),str(ROOT/'test_campaign_v2.py'),str(ROOT/'test_runner_v2.py'),
        str(ROOT/'data/test_prepare_v2.py'),'-q']
    import os
    tests=subprocess.run(command,env={**os.environ,'CUDA_VISIBLE_DEVICES':''},capture_output=True,text=True)
    assert tests.returncode==0,tests.stdout+tests.stderr
    pilot=ROOT/'outputs/pilot-003'
    calls=[json.loads(p.read_text()) for p in pilot.glob('models/*/calls/*.json')]
    episodes=[json.loads(p.read_text()) for p in pilot.glob('models/*/episodes/*.json')]
    status=json.loads((pilot/'STATUS.json').read_text())
    assert len(calls)==54 and all(c['available'] for c in calls)
    assert len({c['response']['request_id'] for c in calls})==54
    assert status['state']=='finished' and not status['failures']
    assert list(pilot.glob('services/*/RELEASED.json'))
    manifest=json.loads((ROOT/'data/MANIFEST_V2.json').read_text())
    assert sha(ROOT/'data/cases-v2.jsonl')==manifest['output']['sha256']
    save('VERIFICATION.json',{'checked':time.time(),'tests_command':command,'returncode':tests.returncode,
        'tests_stdout':tests.stdout,'tests_stderr':tests.stderr,'pilot_calls':len(calls),
        'available_calls':sum(c['available'] for c in calls),'pilot_episodes':len(episodes),
        'excluded_episodes':sum(bool(r.get('excluded')) for r in episodes),
        'available_episodes':sum(r['available'] for r in episodes),'valid_episodes':sum(r['valid'] for r in episodes),
        'pilot_status_sha256':sha(pilot/'STATUS.json'),'source_sha256':{p.name:sha(p) for p in ROOT.glob('*.py')}})
    sources={
        'musique':'/project/alex_phd/research-cache/datasets/musique-v1.0-922ac98f19a201998dbdae6d7f2887a5258dbdeb/musique_data_v1.0.zip',
        'finqa':'/project/alex_phd/research-cache/repos/FinQA-0f16e2867befa6840783e58be38c9efb9229d742/dataset/dev.json',
        'boolq':'/project/alex_phd/research-cache/datasets/boolq-20260911/validation.parquet',
        'ag_news':'/project/alex_phd/research-cache/datasets/fancyzhx--ag_news--eb185aade064a813bc0b7f42de02595523103ca4/test.parquet',
        'longbench_v2':'/project/alex_phd/research-cache/datasets/zai-org--LongBench-v2--2b48e494f2c7a2f0af81aae178e05c7e1dde0fe9/data.json'}
    save('PROVENANCE.json',{'checked':time.time(),'python':platform.python_version(),
        'packages':{p:importlib.metadata.version(p) for p in ('torch','transformers','vllm','tokenizers','psutil')},
        'inputs':{k:{'path':v,'sha256':sha(v),'bytes':Path(v).stat().st_size} for k,v in sources.items()},
        'cases_sha256':sha(ROOT/'data/cases-v2.jsonl'),'data_manifest_sha256':sha(ROOT/'data/MANIFEST_V2.json'),
        'legacy_service_source_sha256':sha(ROOT.parent/'strict-rlm-temperature-adherence-v1/scripts/launch.py'),
        'model_weight_policy':'existing immutable revision-named snapshots; no weight mutation or training'})
    print(json.dumps({'tests_passed':True,'pilot_calls':len(calls),'pilot_episodes':len(episodes)}))
