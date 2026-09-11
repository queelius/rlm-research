"""Authenticate root-only delta and compose prior native proof; READY last."""
import subprocess
import time
import study as s
def prepare():
    if (s.ROOT/'READY.json').exists():raise ValueError('already frozen')
    prior=s.read(s.OLD/'READY.json');s.check(s.OLD/'READY.json','ab16721ee537df09370d534d63fa4d8d542df1e1a17c903efac7c711c1a837d0')
    spec=s.read(s.OLD/'SPEC.json');spec['binding']=s.binding()
    selection=s.CHECKPOINT.parents[2]/'SELECTION.json';selected=s.read(selection)
    if selected['selected_step']!=4 or selected['policy']['adapter_sha256']!=s.NEW_SHA or selected['policy']['path']!=str(s.CHECKPOINT):raise ValueError('not fixed last4')
    pins=dict(prior['source_sha256']);pins[str(s.OLD/'READY.json')]=s.sha(s.OLD/'READY.json')
    for file,expected in [('adapter_model.safetensors',s.NEW_SHA),('adapter_config.json',s.NEW_CONFIG),('state.json','58c0763069ecbc7d3ded04f2f5703d3f1bc1eee3a534280983580a6619ba7270')]:
        p=s.CHECKPOINT/file;s.check(p,expected);pins[str(p)]=expected
    for p in [selection,s.OLD/'ROOT_CONFIG_CAVEAT.md',s.ROOT.parents[1]/'ideas/2026-09-09-next-root-learning-main-approval.md']:pins[str(p)]=s.sha(p)
    tests=subprocess.run([str(s.NATIVE),'-m','unittest','discover','-s',str(s.ROOT),'-p','test_adapter.py','-v'],capture_output=True,text=True)
    s.write(s.ROOT/'CPU_TESTS.json',{'exit_code':tests.returncode,'stdout':tests.stdout,'stderr':tests.stderr,'red':'two missing checkpoint-adapter failures',
        'scope':'actual pinned native role routing; original native six-call runtime proof reused, not rerun','gpu_model_calls':0})
    if tests.returncode:raise ValueError(tests.stderr)
    s.write(s.ROOT/'SPEC.json',spec)
    for p in [*s.ROOT.glob('*.py'),*s.ROOT.glob('*.md'),s.ROOT/'SPEC.json',s.ROOT/'CPU_TESTS.json']:pins[str(p)]=s.sha(p)
    for p,h in pins.items():s.check(p,h)
    s.write(s.ROOT/'READY.json',{'status':'CPU_READY_MAIN_ACCEPTANCE_REQUIRED','prepared_epoch':time.time(),'source_sha256':pins,
        'spec_sha256':s.sha(s.ROOT/'SPEC.json'),'original_ready_sha256':s.sha(s.OLD/'READY.json'),'planned_episodes':32,
        'only_scientific_change':'root checkpoint low66cce to fixed last boundedRL4 2286be; same actual coordinates/seeds/prompts/c32/treatment',
        'caps':spec['caps'],'launch_argv':[str(s.NATIVE),str(s.ROOT/'driver.py'),'run','--output',str(s.ROOT/'outputs/attempt-001')],
        'composed_native_qualification':str(s.OLD/'qualification-002/RESULT.json'),'new_runtime_fixture':False,'gpu_model_calls':0})
if __name__=='__main__':prepare()
