import importlib
from pathlib import Path
import sm_study as s

def test_actual_owner_collector_namespace_and_inventory():
    o=importlib.import_module('sm_owner');c=importlib.import_module('sm_collect')
    args=c.parse_args(o.collector_argv(s.ATTEMPT,1234.)[2:]);o.validate_paths(args)
    assert args.output==s.ATTEMPT/'rollout' and args.binding==s.ATTEMPT/'service/BINDING.json'
    assert len(o.inventory(s.ATTEMPT))==48 and all(r['reward'] is None for r in o.inventory(s.ATTEMPT))
    assert c.implementation().s is s
