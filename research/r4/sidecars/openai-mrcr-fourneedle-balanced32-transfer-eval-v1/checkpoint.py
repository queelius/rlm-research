"""Authenticate fixed cp32 and development-selected LR1e-4 endpoints."""
import importlib.util,sys
from pathlib import Path
import study
RECEIPT=study.ROOT/'ENDPOINTS_FIXED.json'

def _load(label,directory):
    ss=study.load(label+'_study',directory/'study.py'); old=sys.modules.get('study');sys.modules['study']=ss
    try:return ss,study.load(label+'_checkpoint',directory/'checkpoint.py')
    finally:
        if old is None:sys.modules.pop('study',None)
        else:sys.modules['study']=old

cp_study,cp=_load('balanced32_cp32',study.PARENT)
lr_dir=study.SIDE/'openai-mrcr-cp32-fresh8-final-rloo-lr1e4-eval-v1'
lr_study,lr=_load('balanced32_lr1e4',lr_dir)

def verify_checkpoint():
    a=cp.verify_checkpoint(); b=lr.verify_checkpoint()
    ba=cp.binding('checkpoint32'); bb=lr.binding('updated')
    if ba['fixed_child']!=bb['fixed_child'] or ba['models'][ba['fixed_child']]!=bb['models'][bb['fixed_child']]:
        raise ValueError('fixed child differs between arms')
    return {'cp32':a,'lr1e4':b,'bindings':{'cp32':study.digest(ba),'lr1e4':study.digest(bb)}}

def binding(arm):
    if arm=='cp32':return cp.binding('checkpoint32')
    if arm=='lr1e4':return lr.binding('updated')
    raise ValueError('only fixed cp32/lr1e4 arms')
