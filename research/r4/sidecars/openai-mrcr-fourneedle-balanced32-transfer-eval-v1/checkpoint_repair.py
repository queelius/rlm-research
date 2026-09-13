"""Bind unchanged endpoint qualifier to the repaired study namespace."""
import importlib.util,sys
import study_repair as study
old=sys.modules.get('study');sys.modules['study']=study
try:
    spec=importlib.util.spec_from_file_location('balanced32_checkpoint_for_repair',study.ROOT/'checkpoint.py');source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
finally:
    if old is None:sys.modules.pop('study',None)
    else:sys.modules['study']=old
RECEIPT=source.RECEIPT;verify_checkpoint=source.verify_checkpoint;binding=source.binding
