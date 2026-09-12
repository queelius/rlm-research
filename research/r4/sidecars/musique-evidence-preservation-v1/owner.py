"""Reuse exact authenticated V3 service/claim/release; replace only science graph."""
import argparse
import json
from types import ModuleType
import collect
import metrics
import study


def implementation():
    previous=study.load('evidence_qualified_v3_study',study.SERVICE_ROOT/'study_v3.py')
    with study.aliases({'study_v3':previous},study.SERVICE_ROOT):
        lifecycle=study.load('evidence_qualified_v3_lifecycle',study.SERVICE_ROOT/'lifecycle_v3.py')
        with study.aliases({'lifecycle_v3':lifecycle},study.SERVICE_ROOT):
            qualified_owner=study.load('evidence_qualified_v3_owner',study.SERVICE_ROOT/'owner_v3.py')
    source=(study.SERVICE_ROOT/'owner.py').read_text()
    replacements=[("study.ROOT / 'service_wrapper.py'","study.SERVICE_ROOT / 'service_wrapper_v2.py'",2),
                  ("study.ROOT / 'report_worker.py'","study.SERVICE_ROOT / 'report_worker.py'",1),
                  ("study.ROOT / 'READY.json'","study.READY",2),
                  ("        assert (service / 'service/ACTUAL_DISPATCH.json').exists()","        # V3 requires dispatch evidence after real science and cleanup, not warmup.",1),
                  ("        suite.life.__dict__['ALLOCATION_SERVICE'] = suite.SERVE","        suite.life.__dict__['ALLOCATION_SERVICE'] = suite.SERVE\n        lifecycle.install(suite)",1),
                  ("'planned_calls': 132","'planned_calls': 72",1),("'planned_final_slots': 48","'planned_final_slots': 24",1)]
    for stage in ('owner','release','dispatch_qualification'):
        replacements.append(("{'stage': '"+stage+"', 'type': type(error).__name__}","error_record('"+stage+"', error)",1))
    for before,after,count in replacements:
        assert source.count(before)==count,before
        source=source.replace(before,after)
    module=ModuleType('evidence_v3_owner');module.__file__=str(study.SERVICE_ROOT/'owner.py')+':evidence'
    module.lifecycle=lifecycle;module.error_record=qualified_owner.error_record
    with study.aliases({'study':study,'collect':collect,'metrics':metrics},study.ROOT):
        exec(compile(source,module.__file__,'exec'),module.__dict__)
    return module


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['verify','run'])
    parser.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS);a=parser.parse_args()
    if a.command=='verify':print(study.verify()['identity'])
    else:
        result=implementation().execute(a.outer_seconds);print(json.dumps(result));raise SystemExit(0 if result['complete'] else 1)
