"""Add completed decomposition evidence and paired-credit source, excluding raw inputs."""
import hashlib
import importlib.util
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / '2026-09-13-selection-and-state-checkpoint/export.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '7eccd0d04a4ecf54cf8494e1ef26190dd8cfaca2a5a0f1e274a5fd7317fafdda'
spec = importlib.util.spec_from_file_location('decomposition_prior_export', SOURCE)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
exporter = prior.exporter
exporter.__file__ = __file__
exporter.SIDES = ['b05-decision-vector-v1', 'b05-state-representation-v1',
    'b05-singleton-decomposition-v1', 'b05-singleton-decomposition-replica-v1',
    'b05-varied-vector-rollouts-v1']
exporter.ANALYSES = ['b05-decision-vector-independent-2026-09-13',
    'b05-state-representation-independent-2026-09-13',
    'b05-singleton-decomposition-independent-2026-09-13',
    'b05-singleton-replication-independent-2026-09-13',
    'b05-varied-vector-independent-2026-09-13']
exporter.EXTRAS = ['SESSION_CHECKPOINT.md', 'analyses/NOW.md',
    'ideas/2026-09-13-local-credit-prior-art.md',
    'ideas/2026-09-13-learned-routing-after-singletons.md',
    'operations/2026-09-13-decomposition-consolidation/export.py']
store = Path('/project/alex_phd/runs/rlm-research-r4')
for side in exporter.SIDES:
    folder = 'sidecars/' + side
    for name in ('CPU_READY.json', 'READY.json', 'CPU_TESTS.json', 'CPU_TESTS_V2.json',
                 'ADDITIVE_CLARIFICATION.md', 'TRANSPORT_SCORING_ADDENDUM.json',
                 'outputs/attempt-001/RESULT.json', 'outputs/attempt-001/OWNER_TERMINAL.json'):
        if (store / folder / name).is_file():
            exporter.EXTRAS.append(folder + '/' + name)
for analysis in exporter.ANALYSES:
    folder = 'analyses/' + analysis
    for name in ('CPU_READY.json', 'outcome-001/REPORT.json', 'outcome-001/REPORT_V2.json',
                 'outcome-001/SUMMARY.json', 'outcome-001/FINDINGS.md',
                 'outcome-001/INTERPRETATION.md', 'outcome-001/MECHANISM.md',
                 'outcome-001/MECHANISM.json', 'outcome-001/CONFIDENCE.json',
                 'outcome-001/CONFIDENCE.md'):
        if (store / folder / name).is_file():
            exporter.EXTRAS.append(folder + '/' + name)
for version in (1, 2, 3):
    for arm in ('shared', 'local', 'joint'):
        side = f'b05-vector-credit-{arm}-v{version}'
        exporter.SIDES.append(side)
        for name in ('ENTRY_PROOF.json', 'outputs/attempt-001/RESULT.json',
                     'outputs/attempt-001/OWNER_TERMINAL.json',
                     'outputs/attempt-001/checkpoint-0001/state.json',
                     'outputs/attempt-001/checkpoint-0001/EVAL_BINDING.json',
                     'outputs/attempt-001/checkpoint-0001/STEP_COMMIT.json'):
            if (store / 'sidecars' / side / name).is_file():
                exporter.EXTRAS.append('sidecars/' + side + '/' + name)
for operation in ('2026-09-13-decision-vector', '2026-09-13-state-representation',
                  '2026-09-13-singleton-decomposition', '2026-09-13-singleton-replication',
                  '2026-09-13-varied-vector-rollouts', '2026-09-13-paired-vector-credit',
                  '2026-09-13-paired-vector-credit-v3'):
    exporter.EXTRAS.append('operations/' + operation + '/run.py')

if __name__ == '__main__':
    exporter.main()
