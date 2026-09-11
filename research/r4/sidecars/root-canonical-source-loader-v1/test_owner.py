import importlib
from pathlib import Path
import cl_study as s

def test_actual_owner_collector_namespace_and_inventory():
    assert (s.ROOT/'cl_owner.py').exists(), 'owner composition not implemented'
    o=importlib.import_module('cl_owner');c=importlib.import_module('cl_collect')
    args=c.parse_args(o.collector_argv(s.ATTEMPT,1234.)[2:]);o.validate_paths(args)
    assert args.output==s.ATTEMPT/'rollout' and args.binding==s.ATTEMPT/'service/BINDING.json'
    assert len(o.inventory(s.ATTEMPT))==48 and all(r['reward'] is None for r in o.inventory(s.ATTEMPT))
    assert c.implementation().s is s
