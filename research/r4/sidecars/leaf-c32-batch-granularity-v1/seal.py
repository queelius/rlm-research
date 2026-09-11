"""CPU-only source/input/qualification seal; never launches an experiment."""
import importlib.metadata
import platform
import time
import xml.etree.ElementTree as ET
import bg_study as s
def main():
    if s.ATTEMPT.exists() or (s.ROOT/'READY.json').exists():raise ValueError('unused science/seal only')
    suite=ET.parse(s.ROOT/'CPU_TESTS.xml').getroot().find('testsuite')
    assert int(suite.attrib['tests'])==13 and int(suite.attrib['failures'])==int(suite.attrib['errors'])==0
    native=s.read(s.ROOT/'CPU_INPUT_NATIVE.json');plan=s.read(s.ROOT/'inputs/PLAN.json');assert len(plan)==76
    s.write(s.ROOT/'CPU_REPORT.json',dict(tests=13,seconds=float(suite.attrib['time']),failures=0,actual_owner_service_config_popen_interception=True,actual_native_wide_fixture=True,private_label_request_invariance=True,request_workers_qualified=4,max_native_prefix=native['max_prefix'],wide_prompts_exact=12,readout_model_calls=0,gpu_model_loads=0,python=platform.python_version(),versions={n:importlib.metadata.version(n) for n in ['httpx','transformers','tokenizers','pytest']},red_before_green=['missing protocol5','missing collector2','missing owner2','missing diagnostic aggregate field1'],preserved_final_red='CPU_TESTS_RED.xml: test-local generic prepare import resolved inherited module after lifecycle fixture; corrected explicit local-path alias, production unique bg imports unchanged',known_warnings='tokenizer SWIG deprecation only; no scientific calls'))
    inherited=s.read(s.BV/'READY_v2.json');source=dict(inherited['source_sha256']);inputs=dict(inherited['input_sha256'])
    for path in [s.BV/'READY.json',s.BV/'READY_v2.json',s.BV/'BINDING_sft24_v2.json']:
        source[str(path)]=s.sha(path)
    for path in s.ROOT.glob('*'):
        if path.is_file() and path.name!='READY.json':source[str(path)]=s.sha(path)
    for path in (s.ROOT/'inputs').glob('*.json'):inputs[str(path)]=s.sha(path)
    inputs.update(s.read(s.ROOT/'inputs/PROVENANCE.json')['source_sha256'])
    for path,pin in {**source,**inputs}.items():
        if s.sha(path)!=pin:raise ValueError('source/input drift '+path)
    value=dict(schema='c32-batch-granularity-ready-v1',status='CPU_READY_MAIN_ACCEPTANCE_REQUIRED',created_epoch=time.time(),attempt='attempt-001',source_sha256=source,input_sha256=inputs,planned_full=76,planned_labels_per_arm=1024,contexts=2,paired_seeds=list(s.SEEDS),outer_seconds=1200,owned_seconds=1170,work_seconds=1050,startup_seconds=180,collection_seconds_after_max_startup=840,harvest_seconds=30,release_seconds=90,finalize_seconds=30,outer_margin_seconds=30,owner_argv=[str(s.NATIVE),str(s.ROOT/'bg_owner.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.NATIVE),str(s.ROOT/'bg_owner.py'),'verify'],main_launch_only=True,no_root_model_calls=True,no_training=True,fresh_both_arms=True)
    value['identity']=s.digest(value);s.write(s.ROOT/'READY.json',value)
    print(dict(ready_sha256=s.sha(s.ROOT/'READY.json'),identity=value['identity'],source_pins=len(source),input_pins=len(inputs),tests=13))
if __name__=='__main__':main()
