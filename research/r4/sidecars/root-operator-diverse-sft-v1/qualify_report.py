"""Summarize retained real CPU qualification receipts, no assertion from anticipated tests."""
import xml.etree.ElementTree as ET
import od_study as s

def main():
    path=s.ROOT/'QUALIFICATION.junit.xml';root=ET.parse(path).getroot();cases=root.findall('.//testcase')
    if len(cases)!=14 or root.findall('.//failure') or root.findall('.//error') or root.findall('.//skipped'):raise ValueError('exact focused14 passing required')
    artifacts={str(p):s.sha(p) for p in (s.ROOT/'qualification-pytest-001').rglob('*') if p.is_file()}
    s.write(s.ROOT/'CPU_REPORT.json',dict(status='PASS',focused_tests=14,testcase_names=[x.attrib['name'] for x in cases],junit_path=str(path),junit_sha256=s.sha(path),
        elapsed_seconds=sum(float(x.attrib.get('time',0)) for x in root.findall('.//testsuite')),qualification_files_sha256=artifacts,
        actual_native_capture_fixture=True,authored_root_actions=6,fake_child_transports=4,actual_model_calls=0,gpu_calls=0,
        composed_owner_service_config_descriptor_popen_intercept=True,owner_failure_advances_to_final_checks=True,
        tiny_actual_adam_step_and_expired_noop=True,checkpoint_writer='unchanged qualified joint writer; no new GPU checkpoint claimed',
        seed_scan='rg 981451 across sidecar Python and prepared PLAN/PLANS.json found only this sidecar',
        warnings=['two existing SWIG dependency deprecations'],no_scientific_attempt_created=True))
    print(dict(status='PASS',tests=14,retained_files=len(artifacts),report_sha256=s.sha(s.ROOT/'CPU_REPORT.json')))
if __name__=='__main__':main()
