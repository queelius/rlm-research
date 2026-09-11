"""Record MAIN's explicit released-reference choice; no calibration-based selection."""
from pathlib import Path
import od_study as s

def main():
    receipt=s.SIDE/'root-warmstart-reference-v1/outputs/attempt-001/released_reference/service/BINDING.json'
    actual=s.read(receipt);model=actual['models'][actual['role_map']['root']];directory=Path(model['path']);conversion=directory/'CONVERSION.json'
    details=s.read(conversion);base=Path(details['cpu_load_validation']['base_shape_source']);manifest=base/'local-research-manifest.json'
    if not model['adapter_sha256'].startswith('857a7ce6') or details['destination_adapter_sha256']!=model['adapter_sha256']:raise ValueError('exact approved served reference')
    selected=dict(checkpoint=str(directory),adapter_sha256=model['adapter_sha256'],config_sha256=model['config_sha256'],conversion_sha256=s.sha(conversion),step=0,optimizer_state_exists=False)
    s.write(s.ROOT/'inputs/START_BINDING.json',dict(decision='MAIN_APPROVED_START',selection_name='857',selected=selected,
        lineage_receipt_path=str(receipt),lineage_receipt_sha256=s.sha(receipt),conversion_path=str(conversion),conversion_sha256=s.sha(conversion),
        base_path=str(base),base_manifest_path=str(manifest),base_manifest_sha256=s.sha(manifest),source_adapter_path=details['source_path'],source_adapter_sha256=details['source_adapter_sha256'],
        decision_reason='Least-assumption released-reference lineage; not superiority or bare-base equivalence. MAIN approved after exploratory calibration, no best-ancestor selection.',
        exploratory_calibration=dict(released_reference=dict(correct=2,available=8,planned=8),success8=dict(correct=3,available=8,planned=8),interface4=dict(correct=2,available=5,planned=8),all_successes_zero=True,each_nonzero_correct=0,each_nonzero_planned=4,child_calls=0),
        calibration_contexts=['readout-'+f'{i:02}' for i in range(4)],final_contexts=['readout-'+f'{i:02}' for i in range(4,12)],optimizer_origin='fresh Adam; conversion has no fabricated optimizer/state checkpoint'))
    s.starting_policy();print(selected)

if __name__=='__main__':main()
