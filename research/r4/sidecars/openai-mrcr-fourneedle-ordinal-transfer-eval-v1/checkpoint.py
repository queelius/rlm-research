"""Authenticated base and checkpoint32 bindings from the accepted long evaluator."""
import importlib.util
import sys
import study
_old=sys.modules.get("study");sys.modules["study"]=study
try:
    _spec=importlib.util.spec_from_file_location("mrcr_fourneedle_checkpoint_source",study.PARENT/"checkpoint.py")
    source=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(source)
finally:
    if _old is None:sys.modules.pop("study",None)
    else:sys.modules["study"]=_old
RECEIPT=source.RECEIPT
verify_checkpoint=source.verify_checkpoint
binding=source.binding
