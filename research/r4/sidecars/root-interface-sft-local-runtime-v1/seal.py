"""Record focused CPU check and publish amendment READY last."""
import os
import subprocess
import adapter as a

a.verify()
python='/project/alex_phd/envs/prime-rl-5990b1b/bin/python'
argv=[python,'-m','pytest','-q',str(a.ROOT/'test_adapter.py')]
p=subprocess.run(argv,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},text=True,capture_output=True)
if p.returncode:raise ValueError(p.stdout+p.stderr)
a.write(a.ROOT/'TESTS.json',dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,red='3 assertions failed before adapter existed; original terminal output retained',new_native_fixtures=0,gpu_calls=0))
sources={str(p):a.sha(p) for p in list(a.ROOT.glob('*.py'))+list(a.ROOT.glob('*.md'))+[a.ROOT/'TESTS.json',a.PRIOR/'READY.json',a.LOCAL/'CPU_READY.json',a.PRIOR/'qualification-typed-001/RESULT.json',a.LOCAL/'fixture-03/COMPARISON.json']}
ready=dict(schema='root-interface-runtime-only-amendment-ready-v1',status='CPU_READY_FUTURE_ONLY',original_sft_ready_sha256=a.PRIOR_READY,local_runtime_ready_sha256=a.LOCAL_READY,source_sha256=sources,launch_argv=[python,str(a.ROOT/'adapter.py'),'launch','--output',str(a.ROOT/'outputs/attempt-001')],caps={'training_seconds':600,'collection_each_seconds':900,'owned_seconds':3300,'outer_seconds':3330},scientific_recipe_unchanged=True,training_updates=4,evaluation_episodes=48,delta=a.delta(a.ROOT/'outputs/attempt-001'),acceptance_required=True,gpu_calls=0)
a.write(a.ROOT/'READY.json',ready)
print({'READY_sha256':a.sha(a.ROOT/'READY.json'),'adapter_sha256':a.sha(a.ROOT/'adapter.py')})
