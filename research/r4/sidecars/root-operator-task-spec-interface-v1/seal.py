"""Seal stable task-spec72 files after the focused CPU qualification, no rerun."""
from pathlib import Path
import time
import xml.etree.ElementTree as ET
import ts_study as s

def main():
    if (s.ROOT/'READY.json').exists():raise FileExistsError('already sealed')
    suite=ET.parse(s.ROOT/'CPU_TESTS_FINAL.xml').getroot().find('testsuite')
    assert int(suite.attrib['tests'])==6 and all(int(suite.attrib[k])==0 for k in ('errors','failures','skipped'))
    native=s.read(s.ROOT/'CPU_INPUT_NATIVE.json');plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');assert len(native['rows'])==72 and len(plan['full'])==72 and not plan['first_action']
    s.write(s.ROOT/'BINDING_sft24.json',s.binding())
    s.write(s.ROOT/'CPU_REPORT.json',dict(tests=6,failures=0,errors=0,elapsed_seconds=float(suite.attrib['time']),junit_sha256=s.sha(s.ROOT/'CPU_TESTS_FINAL.xml'),native_prefixes=72,private_label_gold_invariance=True,original_file_identity=True,prose_json_equivalence=True,actual_owner_collector_main=True,actual_service_wrapper_popen_intercepted=True,authored_native_root_calls=3,authored_native_child_calls=1,gpu_calls=0,scientific_model_calls=0,test_first_receipt='RED.xml:2failed absent modules; GREEN.xml:2passed; CPU_UNIT.xml:3passed. First combined6:5passed1failed native setup keyword injection. SETUP_RED independently reproduced missing runtime keyword; renamed local parameter only, no input change. Final6 in CPU_TESTS_FINAL.xml.'))
    sources={**s.ss_ready['source_sha256'],str(s.SS/'READY.json'):s.SS_READY_SHA};inputs={**s.ss_ready['input_sha256']}
    receipt=s.read(s.ROOT/'inputs/PROVENANCE.json');inputs.update(receipt['source_sha256']);inputs.update(receipt['seed_inventory_sha256'])
    for name in ('2026-09-10-operator-task-spec-interface72.md','2026-09-10-operator-task-spec-interface72.yaml'):
        path=s.STORE/'ideas'/name;sources[str(path)]=s.sha(path)
    sources.update({str(path):s.sha(path) for path in s.ROOT.iterdir() if path.is_file() and path.name!='READY.json'})
    inputs.update({str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')})
    for directory in ('qualification-001','qualification-final-001'):
        inputs.update({str(path):s.sha(path) for path in (s.ROOT/directory).rglob('*') if path.is_file()})
    for path,pin in {**sources,**inputs}.items():s.dose.check(path,pin)
    ready=dict(schema='operator-task-spec-interface-ready-v1',status='CPU_READY_MAIN_ACCEPTANCE_REQUIRED',source_sha256=sources,input_sha256=inputs,owner_argv=[str(s.NATIVE),str(s.ROOT/'ts_owner.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.NATIVE),str(s.ROOT/'ts_owner.py'),'verify'],work_seconds=3720,owned_seconds=3870,outer_seconds=3900,startup_seconds=180,collection_seconds=3450,harvest_seconds=90,release_emergency_seconds=150,outer_margin_seconds=30,planned_full=72,planned_first_action=0,context_clusters=8,paired_tasks=24,arms=['U','P','J'],policy_order=['sft24'],no_training=True,no_new_external_assets=True,main_launch_only=True,cpu_only=True,created_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);s.verify()
    print(dict(ready_sha256=s.sha(s.ROOT/'READY.json'),identity=ready['identity'],sources=len(sources),inputs=len(inputs),tests=6,seconds=suite.attrib['time']))
if __name__=='__main__':main()
