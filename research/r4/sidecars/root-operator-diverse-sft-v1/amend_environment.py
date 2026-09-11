"""Record approved pre-acceptance environment correction; immutable V1 preserved."""
import json
import subprocess
import od_study as s

def main():
    original=s.read(s.ROOT/'READY.json');mapping=[]
    for name in ('od_study.py','od_binding.py','od_owner.py','test_owner.py','seal.py'):
        path=s.ROOT/name;snapshot=s.ROOT/'pre-acceptance-v1'/(name+'.snapshot' if name.startswith('test_') else name)
        expected=original['source_sha256'][str(path)]
        if s.sha(snapshot)!=expected:raise ValueError('snapshot not byte-identical')
        mapping.append(dict(path=str(path),original_sha256=expected,snapshot=str(snapshot),snapshot_sha256=s.sha(snapshot),corrected_sha256=s.sha(path)))
    code='import json,sys,importlib.metadata as m;from peft import PeftModel;from transformers import AutoModelForCausalLM;print(json.dumps(dict(executable=sys.executable,python=sys.version,versions={k:m.version(k) for k in ("torch","transformers","peft","accelerate","safetensors")})))'
    result=subprocess.run([str(s.TRAIN),'-c',code],capture_output=True,text=True,check=True,timeout=60)
    s.write(s.ROOT/'ENVIRONMENT_AMENDMENT.json',dict(reason='MAIN pre-acceptance review found TRAIN incorrectly equaled native rollout env, which lacks PEFT/Accelerate. No attempt launched; no scientific data changed.',
        authority='MAIN approved exact qualified joint TRAIN correction and V2 READY plumbing',original_ready=str(s.ROOT/'READY.json'),original_ready_sha256=s.sha(s.ROOT/'READY.json'),corrected_ready=str(s.ROOT/'READY_v2.json'),mapping=mapping,
        training_environment=json.loads(result.stdout),native_environment=dict(path=str(s.NATIVE),torch='2.13.0+cu130',transformers='5.6.2',peft=None,accelerate=None,safetensors='0.7.0'),
        qualification='actual TRAIN imports plus composed qualified load module; no 4B model or CUDA load',no_environment_mutation=True,no_inputs_or_protocol_changes=True,all_runtime_ready_refs='READY_v2.json'))
    print(dict(amendment_sha256=s.sha(s.ROOT/'ENVIRONMENT_AMENDMENT.json'),training=str(s.TRAIN)))
if __name__=='__main__':main()
