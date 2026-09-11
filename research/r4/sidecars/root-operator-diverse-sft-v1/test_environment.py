import subprocess
import od_study as s

def test_exact_qualified_training_interpreter_and_real_loader_imports():
    assert s.TRAIN==s.joint().TRAIN and s.TRAIN!=s.NATIVE
    code='import sys;sys.path.insert(0,'+repr(str(s.ROOT))+');import od_study as s;import od_train as t;from peft import PeftModel;from transformers import AutoModelForCausalLM;from types import SimpleNamespace;selected=s.starting_policy();j=s.joint();view=SimpleNamespace(**{**vars(j),"START":s.ROOT.__class__(selected["checkpoint"]),"START_SHA":selected["adapter_sha256"]});old=s.load("od_cpu_actual_train_loader",s.JOINT/"train.py","6491520cf407642f9607413621591cb1dd5c6b139f96c90d784880f4f1f6e405",{"joint_study":view,"joint_learning":t.l});assert old.s.START==view.START;assert old.l.update is t.l.update;print("qualified PEFT/model-loader composition imported; no model loaded")'
    result=subprocess.run([str(s.TRAIN),'-c',code],capture_output=True,text=True,timeout=60)
    assert result.returncode==0,result.stderr
    assert 'no model loaded' in result.stdout
