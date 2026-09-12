"""Both fixed existing models; the completed RL source qualifies their shared parent."""
from functools import lru_cache
from pathlib import Path
import sys
import study

old=sys.modules.get('study');sys.modules['study']=study.prior
try:source=study.load('decode_replica_completed_checkpoint_qualifier',study.PRIOR/'checkpoint.py')
finally:
    if old is None:sys.modules.pop('study',None)
    else:sys.modules['study']=old
RECEIPT=source.RECEIPT
@lru_cache(maxsize=1)
def verify_checkpoint():
    q=source.verify_checkpoint()
    parent=study.read(study.prior.TRAINING/'PARENT_BINDING.json')
    for item in parent['models'].values():
        p=Path(item['path']);assert study.sha(p/'adapter_model.safetensors')==item['adapter_sha256']
        assert study.sha(p/'adapter_config.json')==item['config_sha256']
    return dict(q,cp32_binding_sha256=study.sha(study.prior.TRAINING/'PARENT_BINDING.json'),
                fixed_models=['cp32','updated'],new_training=False)
def binding(arm):
    if arm not in study.CAPS:raise ValueError('only fixed cp32/updated; no best arm')
    verify_checkpoint()
    return (study.read(study.prior.TRAINING/'PARENT_BINDING.json') if arm=='cp32'
            else source.binding('updated'))
