"""CPU-only source/input/native fixture closure; never launches scientific work."""
import xml.etree.ElementTree as ET
import cl_study as s
import cl_protocol as p
import cl_collect as c

def main():
    c.implementation()
    root=ET.parse(s.ROOT/'QUALIFICATION.junit.xml').getroot();cases=root.findall('.//testcase')
    if len(cases)!=8 or root.findall('.//failure') or root.findall('.//error') or root.findall('.//skipped'):raise ValueError('focused8 tests must pass')
    proof=s.read(s.ROOT/'qualification-native-001/RESULT.json')
    if not proof['passed'] or proof['native_calls']!=7 or proof['actual_native_episodes']!=2 or not proof['optional_loader_mutation_then_error_then_reload_verified']:raise ValueError('actual native optional loader qualification')
    for path,pin in proof['source_sha256'].items():s.check(path,pin)
    files={str(path):s.sha(path) for directory in ('qualification-native-001','qualification-pytest-001') for path in (s.ROOT/directory).rglob('*') if path.is_file()}
    report=dict(status='PASS',focused_tests=8,test_names=[v.attrib['name'] for v in cases],
        test_seconds=sum(float(v.attrib.get('time',0)) for v in root.findall('.//testsuite')),
        native_fixture_seconds=proof['elapsed_seconds'],native_episodes=2,native_calls=7,
        actual_model_calls=0,gpu_calls=0,qualification_sha256=files,junit_sha256=s.sha(s.ROOT/'QUALIFICATION.junit.xml'),
        actual_name_error_retained_then_optional_reload=True,common_data_bytes_equal=True,
        no_source_acquisition_post=True,no_environment_mutations=True)
    s.write(s.ROOT/'CPU_REPORT.json',report)
    prior=s.read(s.SM/'READY.json');source=dict(prior['source_sha256']);source[str(s.SM/'READY.json')]=s.sha(s.SM/'READY.json')
    source.update({str(path):s.sha(path) for path in s.ROOT.glob('*') if path.is_file() and path.name!='READY.json'})
    inputs=dict(prior['input_sha256']);inputs.update({str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')})
    inputs[str(p.SOURCE_MANIFEST)]=p.SOURCE_MANIFEST_SHA
    for entry in s.read(s.ROOT/'inputs/REUSED_SOURCES.json'):inputs[entry['path']]=entry['sha256']
    for path,pin in {**source,**inputs}.items():s.check(path,pin)
    value=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,input_sha256=inputs,
        source_collector_counted_edits=c.EDIT_COUNTS,planned_roots=48,planned_source_acquisitions=0,
        reused_acquisitions=8,context_clusters=8,paired_query_blocks=24,work_seconds=1650,owned_seconds=1770,
        outer_seconds=1800,cleanup_seconds=120,outer_margin_seconds=30,startup_seconds=180,root_seconds=1440,closure_seconds=30,
        root_action_tokens=2048,context_tokens=8192,root_grammar=False,
        fixed_root_adapter_sha256=s.binding()['models'][s.binding()['role_map']['root']]['adapter_sha256'],fixed_child_sha256=s.CHILD_SHA,
        primary='strict authentic dataset final',mechanisms='actual source/loader use, faithful map reduction, abandonment/recovery separately audited',
        loader_interface='source_state.load() -> ordinary dict records:list[dict], predictions:dict[str,str]; fresh original copies; no query or reducer',
        historical_sources_not_new_model_work=True,no_current_sft_checkpoint_used=True,
        argv=[str(s.NATIVE),str(s.ROOT/'cl_owner.py'),'run','--output',str(s.ATTEMPT)],
        cpu_report_sha256=s.sha(s.ROOT/'CPU_REPORT.json'),main_acceptance_and_launch_required=True)
    value['identity']=s.digest(value);s.write(s.ROOT/'READY.json',value);s.verify()
    print(dict(identity=value['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),source_pins=len(source),input_pins=len(inputs),tests=8,native_calls=7))

if __name__=='__main__':main()
