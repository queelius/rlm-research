import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
EVIDENCE_SERVICE = (
    ROOT.parent / "root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/service"
)


def test_frozen_inventory_shared_prompt_and_gate_contract():
    import score
    import study

    blocks = study.make_blocks()
    assert len(blocks) == 2
    assert [len(block) for block in blocks] == [6, 6]
    assert [row["family"] for row in blocks[0]] == list(study.FAMILIES)
    assert [row["family"] for row in blocks[1]] == list(study.FAMILIES)
    assert [row["context_id"] for row in blocks[0]] == [
        study.SELECTION[family] for family in study.FAMILIES
    ]
    assert len({row["context_id"] for row in blocks[0]}) == 6
    assert [row["pair_id"] for row in blocks[0]] == [row["pair_id"] for row in blocks[1]]
    prompt = study.common_prompt(study.public()[blocks[0][0]["context_id"]], blocks[0][0]["question"])
    assert "already in your global namespace" in prompt
    assert "reply = await rlm(request_for(batch))" in prompt
    assert 'strict_map(reply.answer, [record["id"] for record in batch])' in prompt
    assert "do not import `rlm`" in prompt
    assert "strict_map(raw, ids)" in prompt
    assert study.common_prompt(study.public()[blocks[0][0]["context_id"]], blocks[0][0]["question"]) == prompt

    rows = []
    for mode in study.MODES:
        for index, family in enumerate(study.FAMILIES):
            rows.append(
                {
                    "coordinate": {"mode": mode, "family": family, "pair_id": str(index)},
                    "endpoint_reward": 1,
                    "invalid_reason": None,
                    "terminal_observable": True,
                    "raw_protocol": {"bad_import_attempts": 0, "max_identical_code_repeats": 1},
                }
            )
    result = score.compute(rows, semantic_request_audit={"parity": True})
    assert result["gate"]["pass"] is True
    rows[0]["raw_protocol"]["bad_import_attempts"] = 1
    assert score.compute(rows, semantic_request_audit={"parity": True})["gate"]["pass"] is False


def test_fresh_process_dependency_request_preparation_and_semantic_audit(tmp_path):
    script = r'''
import json,pathlib,sys
root=pathlib.Path(sys.argv[1]);destination=pathlib.Path(sys.argv[2]);evidence=pathlib.Path(sys.argv[3])
sys.path.insert(0,str(root))
import collect,owner,study
suite=owner.dependencies()
assert all(callable(getattr(suite,name,None)) for name in ('start_service','release_service','command'))
assert pathlib.Path(sys.modules['study'].__file__).resolve()==(root/'study.py').resolve()
(destination/'BINDING.json').write_text((root/'BINDING.json').read_text())
observed={}
for index,mode in enumerate(study.BLOCK_MODES):
    path=destination/(mode+'.json')
    spec=collect.prepare_spec(collect.phase(index,mode),destination/'BINDING.json',
        evidence/'endpoint-original.json',path,123,None)
    observed[mode]={'plans':len(spec['plan']),
        'max_depth':spec['environment']['agent']['harness']['max_depth'],
        'first_id':spec['plan'][0]['id']}

audit=destination/'audit';typed=audit/'typed-audit';role=audit/'role-audit'
typed.mkdir(parents=True);role.mkdir()
for request_id,role_file in (('request-a','role-x'),('request-b','role-y')):
    (typed/(request_id+'-request.json')).write_text('{}')
    (role/(role_file+'-request.json')).write_text(json.dumps({'request_id':request_id}))
semantic=owner.semantic_request_audit(audit)
assert semantic['parity'] and semantic['typed_requests']==semantic['role_requests']==2
print(json.dumps({'observed':observed,'semantic':semantic},sort_keys=True))
'''
    env = {
        **os.environ,
        "CUDA_VISIBLE_DEVICES": "",
        "STRICT_RLM_CALIBRATION_API_KEY": "cpu-fixture-not-used",
    }
    run = subprocess.run(
        [sys.executable, "-c", script, str(ROOT), str(tmp_path), str(EVIDENCE_SERVICE)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    observed = json.loads(run.stdout)["observed"]
    assert observed["no_child"]["plans"] == observed["enabled"]["plans"] == 6
    assert observed["no_child"]["max_depth"] == 0
    assert observed["enabled"]["max_depth"] == 1
    assert observed["no_child"]["first_id"] != observed["enabled"]["first_id"]
