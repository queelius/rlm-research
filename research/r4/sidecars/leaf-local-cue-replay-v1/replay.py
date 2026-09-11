"""Unmodified causal candidate log probabilities; no training or guided decoding."""
import json
import math

def history_prefix(records,position,arm):
    if len(records)!=64 or position not in (16,32,48,64):raise ValueError('fixed context/position required')
    if arm=='matching':tag=records[position-1]['id']
    elif arm=='constant':tag='p0000'
    elif arm=='shifted':tag=records[(position-1+17)%64]['id']
    else:raise ValueError('unknown arm')
    dumps=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':'))
    prior=[dumps({'tag':'p0000','label':r['gold_label']}) for r in records[:position-1]]
    return '['+','.join(prior)+(',' if prior else '')+'{"tag":'+dumps(tag)+',"label":"'

def encode_candidates(tokenizer,prompt_ids,prefix,labels,closing):
    if not prompt_ids or not labels or len(set(labels))!=len(labels):raise ValueError('empty/duplicate candidates')
    bare=tokenizer.encode(prefix,add_special_tokens=False)
    full={label:tokenizer.encode(prefix+label+closing,add_special_tokens=False) for label in labels}
    common=list(bare)
    for ids in full.values():
        size=0
        while size<min(len(common),len(ids)) and common[size]==ids[size]:size+=1
        common=common[:size]
    start=len(prompt_ids)+len(common);candidates={}
    for label,ids in full.items():
        if ids[:len(common)]!=common or len(ids)<=len(common):raise ValueError('not a real common prefix')
        combined=list(prompt_ids)+ids
        if len(combined)>8192:raise ValueError('full candidate exceeds8192; no truncation')
        candidates[label]={'input_ids':combined,'scored_token_ids':ids[len(common):],
            'continuation_text':prefix+label+closing,'complete_input_tokens':len(combined)}
    return {'unmerged_prefix_ids':bare,'shared_output_prefix_ids':common,
        'backed_off_prefix_tokens':len(bare)-len(common),'score_start':start,'candidates':candidates,
        'boundary_rule':'Physical chat IDs fixed; output text encoded whole, back off to prefix shared with every complete candidate'}

def score_candidate(model,input_ids,score_start,device):
    import torch
    if not 1<=score_start<len(input_ids)<=8192:raise ValueError('invalid causal scoring span')
    model.eval();n=len(input_ids)-score_start
    with torch.inference_mode():
        # No current token can predict itself: final token is a target only.
        ids=torch.tensor([input_ids[:-1]],dtype=torch.long,device=device)
        result=model(input_ids=ids,use_cache=False,logits_to_keep=n)
        logits=result.logits[0,-n:].float()
        if logits.shape[0]!=n or not torch.isfinite(logits).all():raise ValueError('nonfinite/incomplete candidate logits')
        targets=torch.tensor(input_ids[score_start:],dtype=torch.long,device=device)
        values=torch.log_softmax(logits,dim=-1).gather(1,targets[:,None]).squeeze(1)
        if not torch.isfinite(values).all():raise ValueError('nonfinite token log probabilities')
        total=values.sum(dtype=torch.float32)
        if not torch.isfinite(total):raise ValueError('nonfinite sequence score')
        return {'token_logprobs':values.cpu().tolist(),'sequence_logprob':float(total.cpu()),
            'scored_tokens':n,'predicted_positions':list(range(score_start,len(input_ids))),
            'conditioning_positions':list(range(score_start-1,len(input_ids)-1)),
            'model_eval':not model.training,'grad_enabled':torch.is_grad_enabled(),'reduction_dtype':'float32'}

def normalize_scores(scores):
    import torch
    if not scores or any(not math.isfinite(v) for v in scores.values()):raise ValueError('nonfinite/empty candidates')
    values=torch.tensor(list(scores.values()),dtype=torch.float32)
    probabilities=torch.softmax(values,dim=0)
    if not torch.isfinite(probabilities).all():raise ValueError('nonfinite normalized probabilities')
    return dict(zip(scores,probabilities.tolist()))
