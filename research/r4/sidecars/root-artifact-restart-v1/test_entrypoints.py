"""Real composed CLI/namespace and planned-missing behavior, no service launches."""
import importlib
from pathlib import Path
import subprocess
import sys
import pytest

def modules():
    assert (Path(__file__).parent/'owner.py').exists(),'missing actual owner'
    assert (Path(__file__).parent/'collect.py').exists(),'missing actual collector'
    return importlib.import_module('owner'),importlib.import_module('collect')

def test_owner_generated_argv_is_accepted_by_actual_collector_namespace(tmp_path):
    owner,collector=modules();stage=tmp_path/'owned-service';destination=tmp_path/'rollout'
    argv=owner.collector_argv(stage,destination,1234.5)
    parsed=collector.parse_args(argv[2:])
    assert Path(argv[1]).name=='collect.py'
    assert parsed.output==destination and parsed.binding==stage/'BINDING.json'
    assert parsed.endpoint==stage/'service/endpoint-original.json' and parsed.deadline==1234.5
    for script in ('owner.py','collect.py'):
        result=subprocess.run([sys.executable,str(Path(__file__).parent/script),'--help'],capture_output=True,text=True)
        assert result.returncode==0,result.stderr

def test_collector_preserves_missing_endpoint_as_null():
    _,collector=modules()
    rows=[dict(id='a'),dict(id='b')]
    result=collector.planned_results(rows,{'a':dict(coordinate=rows[0],reward=0,available=True)})
    assert len(result)==2 and result[0]['reward']==0 and result[1]['reward'] is None

def test_owner_rejects_wrong_namespace_before_creating_output(tmp_path):
    owner,_=modules()
    with pytest.raises(ValueError,match='exact'):owner.check_output(tmp_path/'elsewhere')
    assert not (tmp_path/'elsewhere').exists()
