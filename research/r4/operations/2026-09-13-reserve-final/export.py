"""Publish compact final RL evidence, preserving existing immutable snapshots."""
import hashlib
import importlib.util
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / '2026-09-13-decomposition-consolidation/export.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'c49323249696aad9df2b08470668334c70b5611b95fdd21162070c915806fe96'
spec = importlib.util.spec_from_file_location('final_prior_export', SOURCE)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
exporter = prior.exporter
exporter.__file__ = __file__
store = Path('/project/alex_phd/runs/rlm-research-r4')
exporter.SIDES = [f'b05-vector-credit-held72-eval-v{i}' for i in range(1, 5)] + ['b05-vector-credit-held72-seed2-v1']
exporter.ANALYSES = ['b05-vector-credit-held72-independent-2026-09-13',
    'b05-vector-credit-held72-seed2-independent-2026-09-13']
exporter.EXTRAS = ['SESSION_CHECKPOINT.md', 'RESEARCH_QUEUE.md', 'analyses/NOW.md',
    'analyses/PROMISING_RESULTS.md', 'analyses/CURRENT_SUMMARY.md',
    'operations/2026-09-13-reserve-final/export.py',
    'operations/2026-09-13-reserve-final/HANDOFF.md']
for side in exporter.SIDES:
    for name in ('CPU_TESTS.json', 'BINDING.json', 'CHECKPOINT_QUALIFICATION.json',
                 'outputs/attempt-001/RESULT.json', 'outputs/attempt-001/OWNER_TERMINAL.json'):
        path = store / 'sidecars' / side / name
        if path.is_file():
            exporter.EXTRAS.append(str(path.relative_to(store)))
for analysis in exporter.ANALYSES:
    for path in sorted((store / 'analyses' / analysis).glob('*.json')):
        if path.name in ('RESULTS.json', 'MECHANISM.json', 'COMPARISON.json'):
            exporter.EXTRAS.append(str(path.relative_to(store)))
for name in ('CONFIDENCE.md', 'CONFIDENCE_SUMMARY.json'):
    exporter.EXTRAS.append('analyses/b05-singleton-replication-independent-2026-09-13/outcome-001/' + name)
for operation in ('2026-09-13-vector-credit-held72', '2026-09-13-vector-credit-held72-v4', '2026-09-13-vector-credit-held72-seed2'):
    exporter.EXTRAS.append('operations/' + operation + '/run.py')
if __name__ == '__main__':
    exporter.main()
