"""Unchanged scalar projection/parser/union from qualified singleton176."""
import study as s
assert s.sha(s.PRIOR/'interface.py')=='143bf35fafe99f6f174f7baa70cd74576883962c903e6e3e0fe518058dc74062'
old=s.load('replica_unchanged_scalar_interface',s.PRIOR/'interface.py')
for name in ('singleton_prompt','normalized_public','parse_scalar','singleton_union','unique'):globals()[name]=getattr(old,name)
