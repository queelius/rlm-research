"""The real host/port descriptor must not fail before native generation."""
import importlib
import json
from pathlib import Path

import driver as v1
import pytest

ROOT = Path(__file__).resolve().parent
ENDPOINT = Path('/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-succession/post-leaf-suite-attempt-001/original_old/service/endpoint-original.json')


def test_actual_descriptor_constructs_unchanged_native_context():
    endpoint = json.loads(ENDPOINT.read_text())
    original = json.dumps(endpoint, sort_keys=True)
    case = json.loads((ROOT / 'inputs/PUBLIC.json').read_text())['cases'][0]
    with pytest.raises(KeyError, match='url'):
        v1.context(endpoint, case)
    # Before the amendment this invokes the real broken context, not a mock.
    path = ROOT / 'driver_endpoint_v2.py'
    fixed = importlib.import_module('driver_endpoint_v2') if path.exists() else v1
    actual = fixed.context(endpoint, case)
    expected = v1.context({**endpoint, 'url': 'http://127.0.0.1:18601/v1'}, case)
    assert actual == expected
    assert json.dumps(endpoint, sort_keys=True) == original


def test_actual_six_zero_call_failures_are_not_model_non_submission():
    path = ROOT / 'driver_endpoint_v2.py'
    if not path.exists():
        pytest.fail('operational amendment not implemented')
    fixed = importlib.import_module('driver_endpoint_v2')
    rows = list((ROOT / 'outputs/attempt-001').glob('case-*/EPISODE.json'))
    assert len(rows) == 6
    for path in rows:
        row = json.loads(path.read_text())
        result = fixed.operational_status(row)
        assert result['status'] == 'setup_or_pre_call_failure'
        assert result['model_called'] is False
        assert result['model_non_submission'] is False
