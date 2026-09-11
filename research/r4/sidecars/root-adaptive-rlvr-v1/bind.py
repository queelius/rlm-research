"""Prepare an unapproved exact start candidate; only MAIN may approve its successor."""
import argparse
from pathlib import Path

import study as s


def candidate(kind):
    value = {'approved': False, 'decision_by': 'MAIN', 'kind': kind,
             'campaign_sha256': s.sha(s.ROOT / 'CAMPAIGN.json'),
             'optimizer_origin': 'fresh Adam/RNG, new campaign generation0',
             'note': 'Unapproved candidate only. MAIN freezes choice after SFT readout; no automatic best-validation or fallback.'}
    if kind == 'historical473210':
        prior = s.prior_study()
        files = s.read(s.PRIOR / 'RECIPE.json')['starting_files_sha256']
        value['model'] = {'path': str(prior.START), 'adapter_sha256': s.HISTORICAL_SHA, 'config_sha256': files['adapter_config.json']}
        value['evidence_sha256'] = {str(prior.START / name): expected for name, expected in files.items()}
    elif kind == 'interface_sft_final4':
        path = s.LOCAL / 'outputs/attempt-001/training/RESULT.json'
        result = s.read(path)
        selected = result['selected']
        checkpoint = Path(selected['checkpoint'])
        value.update(result_path=str(path), result_sha256=s.sha(path), selection_sha256=s.sha(path.parent / 'SELECTION.json'),
                     model={'path': str(checkpoint), 'adapter_sha256': selected['adapter_sha256'], 'config_sha256': selected['config_sha256']})
        value['evidence_sha256'] = {str(checkpoint / name): expected for name, expected in result['files_sha256'].items()}
        value['evidence_sha256'].update({str(path): value['result_sha256'],
                                        str(path.parent / 'SELECTION.json'): value['selection_sha256'],
                                        str(checkpoint / 'state.json'): selected['state_sha256']})
    else:
        raise ValueError('unknown named starting family')
    for path, expected in value['evidence_sha256'].items():
        s.check(path, expected)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=('interface_sft_final4', 'historical473210'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    s.verify_prepared()
    s.write(args.output, candidate(args.kind))
    print({'candidate': str(args.output), 'sha256': s.sha(args.output), 'approved': False, 'gpu_calls': 0})
