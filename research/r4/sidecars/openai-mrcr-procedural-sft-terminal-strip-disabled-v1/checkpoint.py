"""Reuse the authenticated, completed cp32 binding; no checkpoint selection."""
from functools import lru_cache
from pathlib import Path
import study

RECEIPT=study.PRIOR/'checkpoint-artifacts/CHECKPOINT_READY.json'
BASELINE_BINDING=study.BASELINE/'owned-service/BINDING.json'


@lru_cache(maxsize=1)
def verify_checkpoint():
    ready=study.read(study.READY)
    if study.sha(RECEIPT)!=ready['checkpoint_receipt_sha256'] or study.sha(BASELINE_BINDING)!=ready['baseline_binding_sha256']:
        raise ValueError('fixed completed checkpoint binding changed')
    receipt=study.read(RECEIPT)
    if receipt.get('identity')!=study.digest({k:v for k,v in receipt.items() if k!='identity'}) or receipt.get('fixed_primary_step')!=32:
        raise ValueError('cp32 qualification receipt differs')
    binding=study.read(BASELINE_BINDING)
    if binding['role_map']!={'root':study.ADAPTED_ALIAS,'children':[study.BASE_ALIAS]}:
        raise ValueError('fixed root/zero-child role differs')
    root=Path(binding['models'][study.ADAPTED_ALIAS]['path'])
    if root!=study.TRAIN_OUTPUT/'checkpoint-0032':
        raise ValueError('fixed resumed cp32 path differs')
    commit=study.read(root/'STEP_COMMIT.json')
    if study.sha(root/'STEP_COMMIT.json')!=ready['checkpoint32_commit_sha256']:
        raise ValueError('cp32 commit differs from preflight qualification')
    for name,want in commit['files_sha256'].items():
        if study.sha(root/name)!=want:raise ValueError('committed cp32 file changed: '+name)
    for alias,model in binding['models'].items():
        path=Path(model['path'])
        if study.sha(path/'adapter_model.safetensors')!=model['adapter_sha256'] or study.sha(path/'adapter_config.json')!=model['config_sha256']:
            raise ValueError('fixed root/child adapter changed: '+alias)
    return receipt


def binding(arm):
    if arm!='checkpoint32':raise ValueError('only fixed checkpoint32 held arm permitted')
    verify_checkpoint()
    return study.read(BASELINE_BINDING)

