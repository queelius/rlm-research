"""Freeze only source/output lifecycle mapping and retained zero-model failure evidence."""
import hashlib
import json
from pathlib import Path
import time
import recovery_wrapper as r

def main():
    old = r.SCIENCE/r.OLD_OUTPUT
    terminal = json.loads((old/'TERMINAL.json').read_text())
    log = old/'teacher-service/launcher.log'
    if terminal['complete'] or terminal['stages'] or any(row['recorded'] for row in terminal['readout_inventory']):
        raise ValueError('failed predecessor contains scientific progress')
    if "KeyError: 'STRICT_RLM_CALIBRATION_API_KEY'" not in log.read_text():
        raise ValueError('not the diagnosed pre-model credential failure')
    if (old/'teacher-service/service/SERVER_START.json').exists() or (old/'capture').exists() or any(old.glob('training-*')):
        raise ValueError('not a zero-model zero-corpus fresh recovery')
    if r.OUTPUT.exists():
        raise ValueError('recovery attempt already exists')
    paths = [r.ROOT/name for name in ('recovery_wrapper.py','test_recovery_wrapper.py','prepare_recovery.py',
        'credential_preflight.py','test_credential_preflight.py','LIFECYCLE_READY_V2.json','CPU_READY.json')]
    paths += [old/'TERMINAL.json',old/'RUN.json',log,r.SCIENCE/'READY.json']
    paths += [r.SCIENCE/name for name in r.COUNTS]
    value = dict(status='PREPARED_FRESH_AFTER_PRE_MODEL_CREDENTIAL_FAILURE',original_scientific_ready_sha256=r.runtime.SCIENTIFIC_READY,
        output=str(r.OUTPUT),prior_output=str(old),original_attempt_preserved=True,original_identity='974c38ad8d0fdbb59f734f7fc2fb8b07e8bb1ac825a868e645ff508ff14a9604',
        source_and_evidence_sha256={str(p):r.runtime.sha(p) for p in paths},
        transformed_source_sha256={name:hashlib.sha256(r.transformed(name).encode()).hexdigest() for name in r.COUNTS},
        output_literal_replacement=dict(before=r.OLD_OUTPUT,after=r.NEW_OUTPUT,counts=r.COUNTS),
        launch_argv_delta='Same NATIVE/TRAIN interpreters, capture/train/readout routed to recovery_wrapper.py command; original flags/caps unchanged',
        checkpoint_policy='Fresh Adam, original low66c start, all complete updates checkpointed; no prior training state exists',
        seed_targets_prompts_data_coefficient_unchanged=True,recovery_is_scientific_reroll=False,
        credential='Parent privately binds existing approved key before verify/run; no value serialized',
        tests=dict(credential_regression_passed=1,recovery_source_and_argv_tests_passed=2),
        prepared_epoch=time.time(),main_parent_acceptance_required=True)
    with (r.ROOT/'RECOVERY_READY.json').open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True)
    print(json.dumps(dict(ready=str(r.ROOT/'RECOVERY_READY.json'),sha256=r.runtime.sha(r.ROOT/'RECOVERY_READY.json'),output=str(r.OUTPUT))))

if __name__ == '__main__':
    main()
