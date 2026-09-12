import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).parent
EVIDENCE_SERVICE = (ROOT.parent / "root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/service")


def test_fresh_process_dependencies_and_both_mode_request_preparation(tmp_path):
    script = r'''
import json,pathlib,sys
root=pathlib.Path(sys.argv[1]);destination=pathlib.Path(sys.argv[2]);evidence=pathlib.Path(sys.argv[3])
sys.path.insert(0,str(root))
import collect_v3,owner_v4,study
suite=owner_v4.dependencies()
assert all(callable(getattr(suite,name,None)) for name in ('start_service','release_service','command'))
assert sys.modules['study'].__file__==str(root/'study.py')
(destination/'BINDING.json').write_text((root/'BINDING.json').read_text())
observed={}
for index,mode in ((0,'no_child'),(1,'enabled')):
    path=destination/(mode+'.json')
    spec=collect_v3.prepare_spec(collect_v3.phase(index,mode),destination/'BINDING.json',
        evidence/'endpoint-original.json',path,123,None)
    observed[mode]={'plans':len(spec['plan']),
        'max_depth':spec['environment']['agent']['harness']['max_depth'],
        'first_id':spec['plan'][0]['id'],'spec_sha256':study.sha(path)}
assert observed['no_child']['plans']==observed['enabled']['plans']==24
assert observed['no_child']['max_depth']==0 and observed['enabled']['max_depth']==1
print(json.dumps(observed,sort_keys=True))
'''
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": "",
        "STRICT_RLM_CALIBRATION_API_KEY": "cpu-fixture-not-used"}
    run = subprocess.run([sys.executable, "-c", script, str(ROOT), str(tmp_path),
        str(EVIDENCE_SERVICE)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stdout + run.stderr
    observed = json.loads(run.stdout)
    assert set(observed) == {"no_child", "enabled"}
    assert observed["no_child"]["first_id"] != observed["enabled"]["first_id"]


def test_attempt002_facade_and_actual_execute_globals():
    import owner_v4
    import study_v4
    assert study_v4.ATTEMPT.name == "attempt-002"
    assert owner_v4.execute.__globals__["dependencies"] is owner_v4.dependencies
    assert owner_v4.execute.__globals__["study"].ATTEMPT == study_v4.ATTEMPT
    assert owner_v4.execute.__globals__["collect"] is owner_v4.collect_v3
