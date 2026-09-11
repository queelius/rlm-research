"""Fail early on absent provider credential before dispatching accepted v3 lifecycle."""
import hashlib
from pathlib import Path
import runpy
from credential_preflight import require_provider_credential

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'study_wrapper_v3.py'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != '4f4e0281b01b319bcaf83b2fedff40d7ebb39419d4ad329ab9d88841ad1adeb2':
    raise ValueError('accepted lifecycle source changed')
require_provider_credential()
runpy.run_path(str(SOURCE), run_name='__main__')
