"""Exact immutable window1 source, fresh cursor and additive V3 seal."""
from pathlib import Path
import warm_study as study
import warm_owner_v2 as qualified

ORIGINAL=study.ROOT/'outputs/attempt-002'
ATTEMPT=study.ROOT/'outputs/attempt-003'
CHARGED_SECONDS=381
PINS={
    'OWNER_TERMINAL.json':'e74c4f048b6958858701e9a2057330578c9d70bf746b81e43913d19e7374700a',
    'window-01/GENERATION.json':'5d97f321a891b49a13f7d017e0b4bd6b87e45b2d56ded495e965ca0aebe4b271',
    'window-01/collection/export/GROUP.json':'0d63be9c9ab89a05d55332f536bd17819c1eebfa4416c486af9e11d51e8fa431',
    'window-01/collection/export/MANIFEST.json':'a38d0fd5da7c3adecde393c64972d1830e02a7f662b0f0dd031c15ede1db9176',
}

def no_previous_readout(output):
    paths=[]
    for directory in Path(output).glob('readout-*'):
        for pattern in ('**/role-audit/*.json','**/typed-audit/*.json','**/physical/*.json','**/episodes/*.json','**/rows/*.json'):
            paths.extend(directory.glob(pattern))
    if paths:raise ValueError('earlier readout dispatch/artifact exists; no reroll authorized')
    return []

def source_proof():
    qualified.verify()
    for path,pin in PINS.items():study.check(ORIGINAL/path,pin)
    if list(ORIGINAL.glob('window-*/TRAIN_COMMAND.json')) or list(ORIGINAL.glob('window-*/training')):
        raise ValueError('prior trainer/update present; not fresh Adam0')
    no_previous_readout(ORIGINAL)
    manifest=study.read(ORIGINAL/'window-01/collection/export/MANIFEST.json')
    generation=study.read(ORIGINAL/'window-01/GENERATION.json')
    if not manifest['complete'] or manifest['planned']!=24 or manifest['recorded']!=24 or manifest['integrity_failures']:
        raise ValueError('original window1 not clean complete24')
    if generation['previous_policy']!=study.fixed_start() or generation['candidate_window']!=1 or generation['round']!=1:
        raise ValueError('original generation not fixed freshAdam0 window1')
    if manifest['generation']!=generation:raise ValueError('manifest generation changed')
    owner=study.read(ORIGINAL/'OWNER_RUN.json')
    return dict(source_attempt=str(ORIGINAL),source_group=str(ORIGINAL/'window-01/collection/export/GROUP.json'),
                source_generation=str(ORIGINAL/'window-01/GENERATION.json'),generation=generation,
                selected=manifest['training_group_episodes'],original_started_epoch=owner['started_epoch'] if 'started_epoch' in owner else owner['started'],
                original_parent_elapsed_seconds=380.0108866,charged_seconds=CHARGED_SECONDS,
                original_readout_dispatches=0,prior_training_commands=0,source_sha256={str(ORIGINAL/p):h for p,h in PINS.items()})

def verify():
    ready=study.read(study.ROOT/'READY_v3.json')
    if study.digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('V3 identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():study.check(path,pin)
    if ready['attempt']!=str(ATTEMPT):raise ValueError('V3 attempt identity')
    proof=source_proof()
    if proof!=study.read(study.ROOT/'RESUME_BINDING_v3.json'):raise ValueError('immutable resume binding differs')
    return ready,proof
