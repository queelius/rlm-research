"""CPU-only immutable preparation receipt; never launches inference or workers."""
import json,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
import rv_study as s
def main():
    if s.ATTEMPT.exists():raise ValueError('scientific attempt already exists')
    test=ET.parse(s.ROOT/'CPU_TESTS.xml').getroot().find('testsuite')
    assert int(test.attrib['tests'])==16 and int(test.attrib['failures'])==int(test.attrib['errors'])==0
    acquisition=s.STORE/'acquisitions/2026-09-10-rlm-official-beb0603.json';receipt=s.read(acquisition)
    commit=subprocess.check_output(['git','-C',str(s.OFFICIAL),'rev-parse','HEAD'],text=True).strip()
    dirty=subprocess.check_output(['git','-C',str(s.OFFICIAL),'status','--porcelain','--untracked-files=normal'],text=True)
    assert commit==receipt['commit'] and not dirty
    s.write(s.ROOT/'CPU_REPORT.json',dict(tests=16,failures=0,errors=0,pytest_seconds=float(test.attrib['time']),junit_sha256=s.sha(s.ROOT/'CPU_TESTS.xml'),official_commit=commit,official_dirty=dirty,actual_isolated_workers=True,actual_native_HTTP_fixture=True,actual_owner_service_Popen_interception=True,gpu_or_model_service_calls=0,model_fit_tested=False,prefix_tokens=[1935,1950],preserved_qualification_directories=['qualification-worker-001','qualification-native-001','qualification-final-001'],generated_epoch=time.time()))
    pins={}
    def add(path,expected=None):
        path=Path(path).resolve();pin=expected or s.sha(path)
        if str(path) in pins and pins[str(path)]!=pin:raise ValueError('conflicting inherited pin '+str(path))
        pins[str(path)]=pin
    for path in s.ROOT.iterdir():
        if path.is_file() and path.name!='READY.json':add(path)
    for path in (s.ROOT/'inputs').rglob('*'):
        if path.is_file():add(path)
    for rootname in ['qualification-worker-001','qualification-native-001','qualification-final-001']:
        for path in (s.ROOT/rootname).rglob('*'):
            if path.is_file():add(path)
    for rel,expected in receipt['tracked_file_sha256'].items():add(s.OFFICIAL/rel,expected)
    add(acquisition)
    for path,pin in s.read(s.ROOT/'inputs/ENVIRONMENT.json')['pure_dependency_sha256'].items():add(path,pin)
    for path,pin in s.read(s.ROOT/'inputs/SOURCE.json').items():add(path,pin)
    for policy,value in s.MODELS.items():
        root=Path(value['path']);manifest=root/'local-research-manifest.json';add(manifest)
        for filename,pin in s.read(manifest)['files'].items():add(root/filename,pin)
    for filename in ['2026-09-10-rlm8b-complete.json','2026-09-10-qwen8b-base-complete.json']:
        add(s.STORE/'acquisitions'/filename)
    for path in [s.SIDE/'leaf-post-sft-suite-v1/MANIFEST.json',s.RUNTIME/'LIFECYCLE_READY_V2.json']:
        add(path)
        for source,pin in s.read(path)['source_sha256'].items():add(source,pin)
    for path in [s.RUNTIME/'CPU_READY.json',s.RUNTIME/'OWNER.json',s.RUNTIME/'PRIVATE_INSPECT.json',s.RUNTIME/'isolation_short.py',s.RUNTIME/'bin/docker',s.RUNTIME/'credential_preflight.py',s.SIDE/'runtime-preinstalled-image-v1/isolation.py',s.SIDE/'rootless-runtime-feasibility-v1/bin/crun-isolated',s.SIDE/'leaf-free-id-correspondence-v1/lifecycle_adapter_v3.py',s.SIDE/'root-rlvr-campaign-v1/campaign_lifecycle_v2.py',s.SIDE/'strict-rlm-temperature-adherence-v1/scripts/launch.py',s.SIDE/'strict-rlm-temperature-adherence-v1/configs/inference-replica0.json',s.PAPER,s.NATIVE,s.NATIVE.with_name('inference'),s.NATIVE.parent.parent/'pyvenv.cfg',s.STORE/'ideas/2026-09-10-published-rlm8b-intended-scaffold.md']:
        add(path)
    ready=dict(schema='published-rlm8b-reference-ready-v1',status='CPU_QUALIFIED_PENDING_MAIN_ACCEPTANCE',planned=48,policies=['base','rlm'],outer_seconds=3600,work_seconds=3330,owned_seconds=3480,owner_argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'verify'],source_sha256=pins,model_bindings=s.MODELS,common_template_sha256=s.sha(s.TEMPLATE),cpu_report_sha256=s.sha(s.ROOT/'CPU_REPORT.json'),launch_authority='MAIN only; no service/GPU/queue started during preparation')
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready)
    print(dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),pins=len(pins),weights_hashed_by_next_actual_owner_verify=True))
if __name__=='__main__':main()
