"""CPU-only immutable source/input/native qualification closure."""
import xml.etree.ElementTree as ET
import sm_study as s
import sm_collect as c

def main():
    root=ET.parse(s.ROOT/'QUALIFICATION.junit.xml').getroot();cases=root.findall('.//testcase')
    if len(cases)!=7 or root.findall('.//failure') or root.findall('.//error') or root.findall('.//skipped'):raise ValueError('focused7 tests must pass')
    proof=s.read(s.ROOT/'qualification-native-001/RESULT.json')
    if not proof['passed'] or proof['native_calls']!=6 or proof['actual_native_episodes']!=2:raise ValueError('actual paired native qualification')
    for path,pin in proof['source_sha256'].items():s.check(path,pin)
    files={str(p):s.sha(p) for directory in ('qualification-native-001','qualification-pytest-001') for p in (s.ROOT/directory).rglob('*') if p.is_file()}
    report=dict(status='PASS',focused_tests=7,test_names=[v.attrib['name'] for v in cases],test_seconds=sum(float(v.attrib.get('time',0)) for v in root.findall('.//testsuite')),native_fixture_seconds=proof['elapsed_seconds'],native_episodes=2,native_calls=6,actual_model_calls=0,gpu_calls=0,qualification_sha256=files,junit_sha256=s.sha(s.ROOT/'QUALIFICATION.junit.xml'),seed_scan='981512 found only this sidecar Python/prepared plan',no_environment_mutations=True)
    s.write(s.ROOT/'CPU_REPORT.json',report)
    prior=s.read(s.CE/'READY.json');source=dict(prior['source_sha256']);source[str(s.CE/'READY.json')]=s.sha(s.CE/'READY.json')
    source.update({str(path):s.sha(path) for path in s.ROOT.glob('*') if path.is_file() and path.name!='READY.json'})
    inputs={str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')}
    inputs.update({str(s.QSR/'inputs'/name):pin for name,pin in s.INPUT_PINS.items()});inputs[str(s.REFERENCE)]=s.REFERENCE_SHA
    for model in s.binding()['models'].values():
        for filename,key in [('adapter_model.safetensors','adapter_sha256'),('adapter_config.json','config_sha256')]:inputs[str(s.ROOT.__class__(model['path'])/filename)]=model[key]
    for path,pin in {**source,**inputs}.items():s.check(path,pin)
    value=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,input_sha256=inputs,source_collector_counted_edits=c.EDIT_COUNTS,
        planned_roots=48,planned_source_acquisitions=8,context_clusters=8,paired_query_blocks=24,work_seconds=2220,owned_seconds=2370,outer_seconds=2400,cleanup_seconds=150,outer_margin_seconds=30,source_seconds=300,root_seconds=1500,root_action_tokens=2048,context_tokens=8192,root_grammar=False,source_grammar='exact public IDs and canonical category domain; no gold',
        fixed_root_adapter_sha256=s.binding()['models'][s.binding()['role_map']['root']]['adapter_sha256'],fixed_child_sha256=s.CHILD_SHA,
        primary='strict authentic dataset final',co_primary='actual supplied-map-consistent executed scoped reduction, separate manual dataflow audit',no_current_sft_checkpoint_used=True,
        argv=[str(s.NATIVE),str(s.ROOT/'sm_owner.py'),'run','--output',str(s.ATTEMPT)],cpu_report_sha256=s.sha(s.ROOT/'CPU_REPORT.json'),main_acceptance_and_launch_required=True)
    value['identity']=s.digest(value);s.write(s.ROOT/'READY.json',value);s.verify();print(dict(identity=value['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),source_pins=len(source),input_pins=len(inputs),tests=7,native_calls=6))
if __name__=='__main__':main()
