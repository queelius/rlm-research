"""Qualified strict scorer, wrong-visible named-record diagnostic only."""
import sys,types
import study as s,protocol as p
path=s.SOURCE/'scoring.py';pin='a0f28f9c4c7e337ec1586343790468a6ea4d5bb670e6e3c54725e16d35d0b596'
if s.sha(path)!=pin:raise ValueError('qualified scorer changed')
source=path.read_text();old="arm=='shift17'"
if source.count(old)!=1:raise ValueError('diagnostic seam changed')
source=source.replace(old,"arm=='wrong'")
module=types.ModuleType('visible_reference_strict_scorer');module.__file__=str(path);sys.modules[module.__name__]=module
with s.aliases({'study':s,'protocol':p}):exec(compile(source,str(path)+'::wrong-visible-diagnostic','exec'),module.__dict__)
missing,score,verified_response=(getattr(module,n) for n in ('missing','score','verified_response'))
