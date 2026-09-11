"""Metadata72 task facade served by the new-corpus checkpoint6."""
import functools
import importlib.util
import sys
from types import SimpleNamespace
import rep_study as rep
import rep_binding

_path = rep.METADATA / "study.py"
_ready = rep.read(rep.METADATA / "READY.json")
_spec = importlib.util.spec_from_file_location("rep_qualified_metadata_study", _path)
metadata = importlib.util.module_from_spec(_spec); sys.modules[_spec.name] = metadata
_spec.loader.exec_module(metadata)
if rep.sha(_path) != _ready["source_sha256"][str(_path)]:
    raise ValueError("qualified metadata study changed")

ROOT = metadata.ROOT
ATTEMPT = rep.ATTEMPT
read, write, sha, digest, load, aliases = rep.read, rep.write, rep.sha, rep.digest, rep.load, rep.aliases
NATIVE = rep.NATIVE


def __getattr__(name): return getattr(metadata, name)
def verify(): return rep.verify()
def binding(arm):
    if arm != "sft6": raise ValueError("new-corpus readout only")
    return rep_binding.binding("new_corpus_sft6")
def validate(value, descriptor, path): return rep_binding.validate(value, descriptor, path)


@functools.lru_cache(maxsize=1)
def stack():
    return metadata.stack()
