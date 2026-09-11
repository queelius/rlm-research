import importlib.util
from pathlib import Path
P=Path(__file__).parent.parent/"root-j1-sufficient-statistics-v1/protocol.py";spec=importlib.util.spec_from_file_location("ss_v2_protocol",P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
unique=m.unique;score=m.score;merge_chunks=m.merge_chunks;native=m.native;reduce_j1=m.reduce_j1

