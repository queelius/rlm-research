"""Publish source and provenance only; exclude cases, raw calls and service credentials."""
import hashlib
import importlib.util
from pathlib import Path
SOURCE=Path(__file__).resolve().parent.parent/'2026-09-13-reserve-final/export.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='3be9afa69d3116db634fd45ec810c772cc59b6bcbbb4feeb0e2744ada8efcf65'
spec=importlib.util.spec_from_file_location('breadth_prior_export',SOURCE)
prior=importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)
exporter=prior.exporter; exporter.__file__=__file__
exporter.SIDES=['unattended-breadth-20260914']; exporter.ANALYSES=[]
exporter.EXTRAS=['SESSION_CHECKPOINT.md','RESEARCH_QUEUE.md','analyses/NOW.md',
    'operations/2026-09-14-unattended-breadth/export.py']
folder='sidecars/unattended-breadth-20260914/'
for name in ('data/prepare.py','data/prepare_v2.py','data/test_prepare.py','data/test_prepare_v2.py',
             'data/MANIFEST.json','data/MANIFEST_V2.json','data/READY_V2.md',
             'LAUNCH.json','VERIFICATION.json','PROVENANCE.json'):
    exporter.EXTRAS.append(folder+name)
if __name__=='__main__': exporter.main()
