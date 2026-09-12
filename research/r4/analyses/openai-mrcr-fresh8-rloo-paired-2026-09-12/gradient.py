"""Saved-gradient vector accounting, not new backprop or counterfactual training."""
import math
import os
from pathlib import Path
import analyze as a

def norm(v):return math.sqrt(math.fsum(float(x.double().square().sum()) for x in v.values()))
def dot(x,y):return math.fsum(float((v.double()*y[n].double()).sum()) for n,v in x.items())

def decompose(post,negative,pre_norm):
    import torch
    factor=min(1.,1./(pre_norm+1e-6))
    parts={'negative_'+key:{n:values.get(n,torch.zeros_like(g)).double()*factor for n,g in post.items()}
           for key,values in negative.items()}
    parts['positive_residual']={n:g.double()-sum(v[n] for v in parts.values()) for n,g in post.items()}
    squared=dot(post,post)
    summary={'clip_factor':factor,'saved_postclip_l2':norm(post),'reported_preclip_l2':pre_norm,
             'components':{},'reconstruction_max_abs_error':max(float((sum(v[n] for v in parts.values())-g).abs().max()) for n,g in post.items())}
    for key,v in parts.items():
        length=norm(v);product=dot(v,post)
        summary['components'][key]={'postclip_l2':length,'preclip_l2_inferred':length/factor,
            'cosine_with_total':product/(length*math.sqrt(squared)) if length else None,
            'signed_gradient_projection_share':product/squared}
    return parts,summary

def run():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    import torch
    from safetensors.torch import load_file
    from transformers import AutoTokenizer
    torch.set_num_threads(2)
    c=a.bindings();s=c.study;q=c.checkpoint.verify_checkpoint();output=s.train.OUTPUT
    data=a.read(s.train.INPUTS);rows=s.train.validate_inputs(data)
    replay=a.read(output/'gradient/REPLAY.json');pre=a.read(output/'PRESTEP_LOGPS.json')
    c.checkpoint.verify_replay(rows,pre,replay)
    gpath=output/'gradient/gradients.pt';npath=output/'gradient/negative-component-gradients.pt'
    g=torch.load(gpath,map_location='cpu',weights_only=True);negative=torch.load(npath,map_location='cpu',weights_only=True)
    parts,vector=decompose(g,negative,replay['gradient_norm_before_clip'])
    initial=torch.load(output/'initial-trainable.pt',map_location='cpu',weights_only=True)
    updated=load_file(str(output/'checkpoint-0001/adapter_model.safetensors'))
    delta={n:updated[n.replace('.default.','.')].double()-v.double() for n,v in initial.items()}
    # Fixed realized step scaling is a descriptive allocation, not an ablation or additive Adam law.
    gains={n:torch.where(v!=0,delta[n]/v.double(),torch.zeros_like(delta[n])) for n,v in g.items()}
    allocations={k:{n:v[n]*gains[n] for n in g} for k,v in parts.items()}
    dnorm=norm(delta);allocation={}
    for k,v in allocations.items():
        length=norm(v);product=dot(v,delta)
        allocation[k]={'allocated_delta_l2':length,
            'cosine_with_realized_delta':product/(length*dnorm) if length else None,
            'signed_delta_projection_share':product/dnorm**2}
    zero_gradient_delta=max(float(delta[n][v==0].abs().max()) if (v==0).any() else 0. for n,v in g.items())
    tok=AutoTokenizer.from_pretrained(str(s.BASE),local_files_only=True)
    token_rows=[]
    for i,row in enumerate(rows):
        if not row['advantage']:continue
        turn=row['root_turns'][0];values=pre['episodes'][i][0];weights=pre['detached_token_weights'][i][0]
        tags=turn['diagnostic_token_parts'];ids=turn['action_ids']
        detail={part:{'tokens':tags.count(part),'HF_chosen_surprisal_sum':-math.fsum(v for v,t in zip(values,tags) if t==part),
                      'native_chosen_surprisal_sum':-math.fsum(v for v,t in zip(turn['old_logprobs'],tags) if t==part)}
                for part in ('body','whitespace','eos')}
        top=[]
        for j in sorted(range(len(values)),key=lambda k:values[k])[:5]:
            text=tok.decode([ids[j]],skip_special_tokens=False)
            top.append({'action_position':j,'distance_from_end':len(ids)-1-j,'token_id':ids[j],'part':tags[j],
                'HF_logprob':values[j],'native_logprob':turn['old_logprobs'][j],'token_TIS_weight':weights[j],
                'token_text_sha256':a.digest(text),'short_token_codepoints':[ord(x) for x in text] if len(text)<=16 else None})
        token_rows.append({'episode_id':row['episode_id'],'group_id':row['group_id'],'reward':row['reward'],
            'advantage':row['advantage'],'parts':detail,'largest_selected_token_surprisals':top,
            'saved_negative_component_gradients':replay['episodes'][i].get('negative_final_component_gradients',{}),
            'positive_token_gradient_components_saved':False})
    old=s.train.OLD/'outputs/attempt-001'
    oldreplay=a.read(old/'gradient/REPLAY.json');oldg=torch.load(old/'gradient/gradients.pt',map_location='cpu',weights_only=True)
    oldn=torch.load(old/'gradient/negative-component-gradients.pt',map_location='cpu',weights_only=True)
    _,oldsummary=decompose(oldg,oldn,oldreplay['gradient_norm_before_clip'])
    for p in (gpath,npath,output/'initial-trainable.pt',output/'checkpoint-0001/adapter_model.safetensors',
              old/'gradient/gradients.pt',old/'gradient/negative-component-gradients.pt'):
        a.PINS[str(p)]=a.sha(p)
    result={'schema':'fresh8-rloo-saved-gradient-decomposition-v1','checkpoint_qualification':q,
        'gradient_vectors':vector,'realized_adapter_delta_l2':dnorm,
        'fixed_realized_step_scaling_allocation':allocation,'zero_gradient_coordinate_max_delta':zero_gradient_delta,
        'allocation_reconstruction_max_abs_error':max(float((sum(v[n] for v in allocations.values())-delta[n]).abs().max()) for n in g),
        'old_fixedbaseline_gradient_vectors':oldsummary,'token_inventory':token_rows,
        'probability_qualification':a.read(output/'PRESTEP_QUALIFICATION.json'),
        'source_sha256':dict(a.PINS),'GPU_calls':0,'backward_calls':0,'optimizer_steps':0,
        'limits':'Negative body/whitespace/EOS gradients were saved separately before clipping. Positive residual is inferred from the clipped total and scaled negative components, with FP32 accumulation/rounding. Positive token-subset gradients were not saved. Signed projection shares can exceed one or be negative because vectors cancel. Realized-step scaling allocation holds the full observed Adam/rounding transformation fixed; it is not the counterfactual update after deleting a component and not rollout causality. Chosen logprobs give surprisal, not full-distribution entropy. Old and new batches, advantages and norms differ.'}
    a.write(a.ROOT/'GRADIENT.json',result)
    lines=['# Saved-gradient accounting','',
        f"Fresh total preclip {vector['reported_preclip_l2']:.8g}; saved postclip {vector['saved_postclip_l2']:.8g}; clip factor {vector['clip_factor']:.8g}. Realized adapter delta {dnorm:.8g}.",
        f"Old fixed-baseline preclip {oldsummary['reported_preclip_l2']:.8g}; distinct source batch and objective.",'']
    for k,v in vector['components'].items():
        lines.append(f"{k}: inferred preclip L2 {v['preclip_l2_inferred']:.8g}; signed projection on full gradient {v['signed_gradient_projection_share']:.5f}; cosine {v['cosine_with_total']}.")
    lines+=['',result['limits']]
    a.write(a.ROOT/'GRADIENT.md','\n'.join(lines)+'\n')
    print({'gradient_report':str(a.ROOT/'GRADIENT.json'),'preclip_norm':vector['reported_preclip_l2'],'postclip_norm':vector['saved_postclip_l2']})
    return result

if __name__=='__main__':run()
