"""Original-weight binding must be explicit and change no model input fields."""
import importlib
import json
from copy import deepcopy
from pathlib import Path

import driver as v1
import pytest

ROOT = Path(__file__).resolve().parent
ENDPOINT = ROOT.parents[1] / 'operations/2026-09-09-succession/post-leaf-suite-attempt-001/original_old/service/endpoint-original.json'


def test_original_binding_accepts_real_descriptor_without_nonmodel_request_changes():
    original = json.loads((ROOT / 'SPEC.json').read_text())
    descriptor = json.loads(ENDPOINT.read_text())
    if not (ROOT / 'driver_original_weight.py').exists():
        # Real pre-amendment rejection is the RED boundary.
        v1.bind_identity(original, descriptor)
    module = importlib.import_module('driver_original_weight')
    bound = module.bind_identity(original, descriptor)
    for key, body in bound['requests'].items():
        expected = deepcopy(original['requests'][key])
        expected['model'] = descriptor['model_alias']
        assert body == expected
    design = deepcopy(bound['design'])
    design['model_alias'] = original['design']['model_alias']
    assert design == original['design']
    assert bound['weights']['adapter'] == descriptor['adapter']
    assert module.correct_attempt({'adapter_sha256': 'old'})['adapter_sha256'] == descriptor['adapter']['model_sha256']


def test_wrong_adapter_and_live_root_are_rejected():
    if not (ROOT / 'driver_original_weight.py').exists():
        pytest.fail('original-weight amendment absent')
    module = importlib.import_module('driver_original_weight')
    descriptor = json.loads(ENDPOINT.read_text())
    bad = deepcopy(descriptor)
    bad['adapter']['model_sha256'] = 'c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3'
    with pytest.raises(ValueError):
        module.validate_endpoint(bad)
    card = {'id': descriptor['model_alias'], 'root': descriptor['adapter']['path'], 'parent': descriptor['base_model']['path']}
    base = {'id': descriptor['base_model']['path'], 'max_model_len': 8192}
    module.validate_live_models(descriptor, {'data': [card, base]})
    with pytest.raises(ValueError):
        module.validate_live_models(descriptor, {'data': [{**card, 'root': '/wrong'}, base]})
