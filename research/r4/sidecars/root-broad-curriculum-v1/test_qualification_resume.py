import importlib
import importlib.metadata
from pathlib import Path

import pytest


def test_only_absent_native_peft_is_recorded_not_hidden():
    assert (Path(__file__).parent/'qualify_metadata_resume.py').exists(), 'metadata resume absent'
    m=importlib.import_module('qualify_metadata_resume')
    def missing(name): raise importlib.metadata.PackageNotFoundError(name)
    assert m.native_version('peft',missing)=='not installed in native serving interpreter'
    with pytest.raises(importlib.metadata.PackageNotFoundError): m.native_version('torch',missing)
    assert m.native_version('torch',lambda name:'2.13.0')=='2.13.0'
