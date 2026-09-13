"""Add compact completed evidence; never publish raw model inputs or weights."""
import hashlib
import importlib.util
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / '2026-09-12-dose-and-delegation-checkpoint/export.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '0bd2ff05d26a04efcc714a257726cf9a771e15ac96f4fd8a5194b28db09d8395'
spec = importlib.util.spec_from_file_location('selection_state_prior_export', SOURCE)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
exporter = prior.exporter
exporter.__file__ = __file__
# Extend only the total publication budget, not per-file or credential guards.
# Do not mutate any previously executed exporter or immutable research source.
source = prior.prior.prior.source
assert source.count('if total > 64 * 1024**2:') == 1
source = source.replace('if total > 64 * 1024**2:', 'if total > 96 * 1024**2:')
source = source.replace('Explicit sealed September12 sidecars and selected reports',
                        'Explicit sealed September13 sidecars and completed reports')
exec(compile(source, __file__, 'exec'), exporter.__dict__)

exporter.SIDES = [
    'openai-mrcr-fourneedle-balanced32-transfer-data-v1',
    'openai-mrcr-fourneedle-balanced32-transfer-eval-v1',
    'b05-flat-selection-rl-v1', 'b05-flat-selection-rl-eval-v1',
    'b05-flat-selection-rl-dose10-v1', 'b05-flat-selection-rl-dose10-eval-v1',
    'b05-selection-id-renaming-v1', 'b05-public-normalization-held9-v1',
    'b05-public-normalization-fresh12-v1', 'b05-qwen3-8b-direct-oracle-v1',
    'finqa-two-example-interface-v1', 'finqa-two-example-fresh16-v1',
]
exporter.ANALYSES = [
    'openai-mrcr-fourneedle-balanced32-dose-transfer-2026-09-12',
    'b05-flat-selection-rl-independent-2026-09-13',
    'b05-flat-selection-rl-dose10-independent-2026-09-13',
    'b05-selection-id-renaming-audit-2026-09-13',
    'b05-public-normalization-independent-2026-09-13',
    'b05-public-normalization-fresh12-independent-2026-09-13',
    'b05-qwen3-8b-alternative-model-2026-09-13',
    'finqa-two-example-independent-2026-09-12',
    'finqa-two-example-fresh16-independent-2026-09-13',
]
exporter.EXTRAS = [
    'SESSION_CHECKPOINT.md', 'analyses/NOW.md',
    'questions/public-state-and-decision-accounting.md',
    'ideas/2026-09-13-normalize-public-state-before-delegation.md',
    'ideas/2026-09-13-selection-rules-or-record-identities.md',
    'ideas/2026-09-12-helper-count-is-not-input-size.md',
    'analyses/root-published-rlm8b-port-assessment-2026-09-12/MODEL_CHARACTERIZATION_CORRECTION.md',
    'operations/2026-09-13-selection-and-state-checkpoint/export.py',
    'operations/2026-09-13-selection-and-state-checkpoint/HANDOFF.md',
    'operations/2026-09-13-b05-alternative-model/CLEANUP.md',
    'operations/2026-09-13-b05-alternative-model/OWNED_SIGTERM.json',
    'operations/2026-09-13-b05-alternative-model/terminate_owned.py',
]
groups = {
    'analyses/openai-mrcr-fourneedle-balanced32-dose-transfer-2026-09-12':
        ['CPU_READY_V2.json', 'outcome-002/RESULTS.json', 'outcome-002/RESULTS.md'],
    'analyses/b05-flat-selection-rl-independent-2026-09-13':
        ['CPU_READY.json', 'readout-001.json'],
    'analyses/b05-flat-selection-rl-dose10-independent-2026-09-13':
        ['CPU_READY.json', 'readout-001.json'],
    'analyses/b05-selection-id-renaming-audit-2026-09-13': ['RESULTS.json'],
    'analyses/b05-public-normalization-independent-2026-09-13':
        ['CPU_READY.json', 'outcome-001/FINDINGS.md', 'outcome-001/REPORT.json',
         'outcome-001/MECHANISM_REVIEW.json'],
    'analyses/b05-public-normalization-fresh12-independent-2026-09-13':
        ['CPU_READY.json', 'outcome-001/FINDINGS.md', 'outcome-001/REPORT.json',
         'outcome-001/SUMMARY.json', 'outcome-001/MECHANISM_REVIEW.json',
         'outcome-001/MECHANISM_RECEIPT.json'],
    'analyses/b05-qwen3-8b-alternative-model-2026-09-13':
        ['CPU_READY.json', 'RESULTS.json', 'SELECTION_WITNESS_DIAGNOSTIC.json'],
    'analyses/finqa-two-example-independent-2026-09-12':
        ['CPU_READY.json', 'outcome-001/FINDINGS.md', 'outcome-001/COMPARISON.json',
         'outcome-001/MECHANISM_REVIEW.json'],
    'analyses/finqa-two-example-fresh16-independent-2026-09-13':
        ['CPU_READY.json', 'outcome-002/FINDINGS.md', 'outcome-002/RESULT.json',
         'outcome-002/MECHANISM_REVIEW.json'],
    'sidecars/openai-mrcr-fourneedle-balanced32-transfer-data-v1': ['DATA_READY.json'],
    'sidecars/openai-mrcr-fourneedle-balanced32-transfer-eval-v1':
        ['RUN_READY_SERVICE_REPAIR.json', 'CPU_TESTS_SERVICE_REPAIR.json',
         'outputs/cp32-001/OWNER_TERMINAL.json', 'outputs/lr1e4-001/OWNER_TERMINAL.json',
         'outputs/cp32-002/OWNER_TERMINAL.json', 'outputs/lr1e4-002/OWNER_TERMINAL.json'],
    'sidecars/b05-public-normalization-held9-v1': ['CPU_READY.json'],
    'sidecars/b05-public-normalization-fresh12-v1': ['CPU_READY.json', 'CPU_TESTS_V2.json'],
    'sidecars/b05-selection-id-renaming-v1': ['DATA_READY.json'],
    'sidecars/finqa-two-example-interface-v1': ['CPU_READY.json'],
    'sidecars/finqa-two-example-fresh16-v1': ['CPU_READY.json'],
    'sidecars/b05-qwen3-8b-direct-oracle-v1':
        ['outputs/attempt-002/OWNER_TERMINAL.json', 'outputs/attempt-003/OWNER_TERMINAL.json',
         'CPU_TESTS_LIFECYCLE_REPAIR.json'],
}
for side in exporter.SIDES:
    folder = 'sidecars/' + side
    if side not in ('openai-mrcr-fourneedle-balanced32-transfer-data-v1',
                    'openai-mrcr-fourneedle-balanced32-transfer-eval-v1',
                    'b05-qwen3-8b-direct-oracle-v1'):
        groups.setdefault(folder, []).append('outputs/attempt-001/OWNER_TERMINAL.json')
for side in ('b05-flat-selection-rl-v1', 'b05-flat-selection-rl-dose10-v1'):
    groups.setdefault('sidecars/' + side, []).extend([
        'outputs/attempt-001/checkpoint-0001/state.json',
        'outputs/attempt-001/checkpoint-0001/STEP_COMMIT.json',
        'outputs/attempt-001/checkpoint-0001/EVAL_BINDING.json',
    ])
for folder, names in groups.items():
    exporter.EXTRAS.extend(folder + '/' + name for name in names)
for operation in ('2026-09-12-fresh32-dose-transfer-repair',
                  '2026-09-13-selection-rl-and-fresh-finqa',
                  '2026-09-13-selection-rl-readout',
                  '2026-09-13-normalization-and-model-control',
                  '2026-09-13-selection-dose10', '2026-09-13-selection-dose10-readout',
                  '2026-09-13-selection-id-renaming', '2026-09-13-normalization-fresh12'):
    exporter.EXTRAS.append('operations/' + operation + '/run.py')

if __name__ == '__main__':
    exporter.main()
