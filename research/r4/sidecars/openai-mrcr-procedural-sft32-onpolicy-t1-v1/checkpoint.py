"""Unchanged authenticated checkpoint32 binding."""
import importlib.util,sys
from pathlib import Path
import study
ROOT=Path(__file__).resolve().parent;_old=sys.modules.get('study');sys.modules['study']=study
try:
    s=importlib.util.spec_from_file_location('mrcr_t1_checkpoint_source',study.SOURCE_SCREEN/'checkpoint.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
finally:
    if _old is None:sys.modules.pop('study',None)
    else:sys.modules['study']=_old
RECEIPT=m.RECEIPT;verify_checkpoint=m.verify_checkpoint;binding=m.binding
