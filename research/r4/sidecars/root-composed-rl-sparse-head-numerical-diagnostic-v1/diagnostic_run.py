"""No-optimizer dense/dense/sparse gradient measurement on the frozen short turn."""
import argparse,json,os,signal,sys,time
from pathlib import Path
import diagnostic_math as dm
import diagnostic_study as study
sys.path.insert(0,str(study.SPARSE));import sparse_math  # noqa:E402
sys.path.insert(0,str(study.SOURCE));import terminal_common as common  # noqa:E402
import terminal_train as original  # noqa:E402

def grad(model):
    import torch
    values=[p.grad.detach().float().reshape(-1).cpu() for n,p in model.named_parameters() if p.requires_grad and p.grad is not None]
    if not values:raise ValueError("missing LoRA gradients")
    return torch.cat(values)
def prepare_model(model):
    import torch
    model.train();model.config.use_cache=False;model.enable_input_require_grads();model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant":False})
    for module in model.modules():
        if isinstance(module,torch.nn.Dropout):module.eval()
    if any("lora_" not in n or p.dtype!=torch.float32 for n,p in model.named_parameters() if p.requires_grad):raise ValueError("FP32 LoRA only")
def run(args):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM
    study.verify_inputs();group,generation,identity=original.authenticate_group(args.group,args.generation)
    if args.group.resolve()!=study.GROUP.resolve() or args.generation.resolve()!=study.GENERATION.resolve() or args.checkpoint.resolve()!=study.CHECKPOINT.resolve():raise ValueError("exact failed group only")
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or not torch.cuda.is_available() or torch.cuda.device_count()!=1:raise ValueError("exactly one assigned GPU")
    cap=min(270,args.deadline-time.time());started=time.monotonic();prior=signal.signal(signal.SIGALRM,lambda *_:(_ for _ in()).throw(TimeoutError("diagnostic cap")));signal.setitimer(signal.ITIMER_REAL,max(.001,cap))
    try:
        recipe=study.read(study.SOURCE/"RECIPE.json")
        base=AutoModelForCausalLM.from_pretrained(recipe["base_model"],local_files_only=True,dtype=torch.bfloat16,attn_implementation="sdpa",device_map={"":"cuda:0"})
        model=PeftModel.from_pretrained(base,args.checkpoint,is_trainable=True,autocast_adapter_dtype=True);prepare_model(model)
        turns=[(t,e["advantage"]) for e in group["episodes"] for t in e["turns"]];turn,adv=min(turns,key=lambda z:len(z[0]["input_ids"]));tis=common.c.pilot_math().tis_module()
        ids=torch.tensor([turn["input_ids"]],dtype=torch.long,device=model.device);captures={};vectors={}
        for name,kind in (("dense_a","dense"),("dense_b","dense"),("sparse","sparse")):
            model.zero_grad(set_to_none=True)
            if kind=="dense":
                logits=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False).logits
                loss,capture=tis.tis_action_loss(logits,turn,advantage=adv,temperature=recipe["temperature"])
            else:
                positions=torch.tensor(sparse_math.position_list(turn),dtype=torch.long,device=model.device)
                logits=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=positions).logits
                loss,capture=sparse_math.selected_tis_loss(logits,turn,advantage=adv,temperature=recipe["temperature"],tis=tis)
            loss.backward();torch.cuda.synchronize();vectors[name]=grad(model);captures[name]={"loss":float(loss.detach().cpu()),"hf_old_logprobs":capture["hf_old_logprobs"]}
            torch.save(vectors[name],args.output/f"gradient-{name}.pt")
        comparisons={"dense_a_vs_dense_b":dm.compare(vectors["dense_a"],vectors["dense_b"]),"dense_a_vs_sparse":dm.compare(vectors["dense_a"],vectors["sparse"])}
        result={"schema":"sparse-head-gradient-numerical-diagnostic-v1","optimizer_constructed":False,"optimizer_steps":0,"sequence_tokens":len(turn["input_ids"]),"action_tokens":len(turn["old_logprobs"]),"captures":captures,"comparisons":comparisons,"input_identity":identity["input_identity"],"elapsed_seconds":time.monotonic()-started}
        result["gradient_sha256"]={n:study.sha(args.output/f"gradient-{n}.pt") for n in vectors};study.write(args.output/"RESULT.json",result);return result
    finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,prior)
def parse_args(argv=None):
    p=argparse.ArgumentParser();p.add_argument("--group",type=Path,required=True);p.add_argument("--generation",type=Path,required=True);p.add_argument("--checkpoint",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--deadline",type=float,required=True);return p.parse_args(argv)
if __name__=="__main__":print(json.dumps(run(parse_args()),sort_keys=True,allow_nan=False))
