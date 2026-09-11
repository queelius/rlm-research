"""Unchanged native physical root/typed-child reconstruction; new union verifier CLI."""
import argparse
import json
import functools
from pathlib import Path
import study as s
impl=s.private('native.py',{'study':s})
@functools.lru_cache(maxsize=1)
def stack():
    with s.aliases({}):return impl.stack()
exact_turns=impl.exact_turns;validate_typed_audit=impl.validate_typed_audit
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify-export',));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    from export import authenticate_export
    print(json.dumps(authenticate_export(a.output),sort_keys=True))
