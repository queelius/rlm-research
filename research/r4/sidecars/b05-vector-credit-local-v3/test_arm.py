"""Regression: owner-created output is accepted and model loading is never reached on CPU."""
import study

class Sentinel(Exception):pass

def test_owner_created_directory_reaches_patched_model_sentinel(monkeypatch,tmp_path):
    import torch,train,transformers
    ready,rows=train.preflight();assert ready["credit_mode"]=="local" and len(rows)==64
    output=tmp_path/"attempt";output.mkdir();study.write_x(output/"OWNER_START.json",{"fixture":True})
    monkeypatch.setattr(study,"OUTPUT",output);monkeypatch.setenv("CUDA_VISIBLE_DEVICES","CPU_SENTINEL")
    monkeypatch.setattr(torch.cuda,"device_count",lambda:1)
    monkeypatch.setattr(torch.cuda,"manual_seed_all",lambda _seed:None)
    monkeypatch.setattr(torch.cuda,"empty_cache",lambda:None)
    def stop(*_args,**_kwargs):raise Sentinel("MODEL_LOAD_SENTINEL")
    monkeypatch.setattr(transformers.AutoModelForCausalLM,"from_pretrained",stop)
    try:train.trainer.run(study,output,study.SCIENCE_SECONDS)
    except Sentinel as error:assert str(error)=="MODEL_LOAD_SENTINEL"
    else:raise AssertionError("model-loader sentinel not reached")
    assert study.read(output/"RESULT.json")["error"]["message"]=="MODEL_LOAD_SENTINEL"
    assert (output/"START.json").exists() and (output/"OWNER_START.json").exists()
