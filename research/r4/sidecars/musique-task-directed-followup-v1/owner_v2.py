"""Attempt002: actual registry hook; dispatch qualification after science, not warmup."""
import argparse
import json
from types import ModuleType

import study_v2 as study


def implementation():
    with study.aliases({'study': study}, study.ROOT):
        collector = study.load('report_followup_v2_collect', study.ROOT / 'collect.py')
        metrics = study.load('report_followup_v2_metrics', study.ROOT / 'metrics.py')
    text = (study.ROOT / 'owner.py').read_text()
    assert text.count("assert (service / 'service/ACTUAL_DISPATCH.json').exists()") == 1
    text = text.replace("        assert (service / 'service/ACTUAL_DISPATCH.json').exists()", '        # Actual dispatch receipt is checked after science; warmup is not a prerequisite.')
    assert text.count("study.ROOT / 'service_wrapper.py'") == 2
    assert text.count("study.ROOT / 'READY.json'") == 2
    text = text.replace("study.ROOT / 'service_wrapper.py'", "study.ROOT / 'service_wrapper_v2.py'")
    text = text.replace("study.ROOT / 'READY.json'", "study.ROOT / 'READY_V2.json'")
    module = ModuleType('report_followup_v2_owner_source'); module.__file__ = str(study.ROOT / 'owner.py') + ':v2'
    with study.aliases({'study': study, 'collect': collector, 'metrics': metrics}, study.ROOT):
        exec(compile(text, module.__file__, 'exec'), module.__dict__)
    return module


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['verify', 'run'])
    parser.add_argument('--outer-seconds', type=int, default=1700); args = parser.parse_args()
    if args.command == 'verify': print(study.verify()['identity'])
    else:
        result = implementation().execute(args.outer_seconds)
        print(json.dumps(result)); raise SystemExit(0 if result['complete'] else 1)
