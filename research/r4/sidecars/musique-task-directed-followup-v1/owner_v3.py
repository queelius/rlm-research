"""V2 science plus exact lifecycle command; sanitized failure detail, no retries."""
import argparse
import json
import os
import traceback
from types import ModuleType

import lifecycle_v3 as lifecycle
import study_v3 as study


def error_record(stage, error):
    message, trace = str(error), traceback.format_exc()
    for key, value in os.environ.items():
        if len(value) >= 6 and any(part in key.upper() for part in ('API_KEY', 'TOKEN', 'SECRET', 'PASSWORD')):
            message, trace = message.replace(value, '[REDACTED]'), trace.replace(value, '[REDACTED]')
    return {'stage': stage, 'type': type(error).__name__, 'message': message,
            'traceback': trace, 'traceback_locals_included': False}


def implementation():
    with study.aliases({'study': study}, study.ROOT):
        collector = study.load('report_followup_v3_collect', study.ROOT / 'collect.py')
        metrics = study.load('report_followup_v3_metrics', study.ROOT / 'metrics.py')
    source = (study.ROOT / 'owner.py').read_text()
    changes = [
        ("        assert (service / 'service/ACTUAL_DISPATCH.json').exists()",
         '        # Final real dispatch qualification remains mandatory; warmup is not required.', 1),
        ("study.ROOT / 'service_wrapper.py'", "study.ROOT / 'service_wrapper_v2.py'", 2),
        ("study.ROOT / 'READY.json'", "study.ROOT / 'READY_V3.json'", 2),
        ("        suite.life.__dict__['ALLOCATION_SERVICE'] = suite.SERVE",
         "        suite.life.__dict__['ALLOCATION_SERVICE'] = suite.SERVE\n        lifecycle.install(suite)", 1)]
    for stage in ('owner', 'release', 'dispatch_qualification'):
        changes.append(("{'stage': '" + stage + "', 'type': type(error).__name__}",
                        "error_record('" + stage + "', error)", 1))
    for before, after, count in changes:
        assert source.count(before) == count, before
        source = source.replace(before, after)
    module = ModuleType('report_followup_v3_owner_source'); module.__file__ = str(study.ROOT / 'owner.py') + ':v3'
    module.lifecycle, module.error_record = lifecycle, error_record
    with study.aliases({'study': study, 'collect': collector, 'metrics': metrics}, study.ROOT):
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['verify', 'run'])
    parser.add_argument('--outer-seconds', type=int, default=1700); args = parser.parse_args()
    if args.command == 'verify': print(study.verify()['identity'])
    else:
        result = implementation().execute(args.outer_seconds)
        print(json.dumps(result)); raise SystemExit(0 if result['complete'] else 1)
