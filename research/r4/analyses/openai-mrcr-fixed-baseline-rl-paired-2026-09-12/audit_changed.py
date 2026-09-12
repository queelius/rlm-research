"""Additive exact changed-output audit; raw final strings remain in a 0600 local receipt."""
import json
import math
import os
from pathlib import Path
from difflib import SequenceMatcher
import analyze as a

def run():
    source=a.ROOT/'readout-002.json';assert a.sha(source)=='4ac83a409099ca5af87d6f433e0872041e7ef5779c71378d5c1a21fff6473e85'
    r=a.read(source);s=a.bindings().study;rows=[];private=[];first_equal=0;count=0
    for phase,x in r['phases'].items():
        records={z['id']:z for z in s.prior(phase).records(phase)}
        for pair in x['pairing']['pairs']:
            ident=pair['coordinate']['id'];left=x['cp32']['rows'][ident];right=x['updated']['rows'][ident]
            first_equal+=bool(left['native_actions'] and right['native_actions'] and all(left['native_actions'][0][k]==right['native_actions'][0][k] for k in ('prompt_sha256','action_sha256')));count+=1
            if pair['native_token_paths_equal_descriptive_only']:continue
            loaded=[]
            for prior_row in (left,right):
                p=Path(prior_row['episode_path']);episode=a.read(p);trace=episode['episode']['traces'][0]
                native=[]
                for np in sorted((p.parents[1]/'native-calls').glob('*-result.json')):
                    value=json.loads(np.read_text())
                    if value.get('session_id')==trace['id']:
                        a.PINS[str(np)]=a.sha(np);native.append(value)
                loaded.append((episode,trace,native))
            (old,ot,on),(new,nt,nn)=loaded;gold=old['derived']['answer'];old_text=ot['root_reply'];new_text=nt['root_reply']
            assert gold==new['derived']['answer'] and a.digest(old_text)==left['final_sha256'] and a.digest(new_text)==right['final_sha256']
            truth=a.read(s.input_dir(phase)/'HOST_GOLD.json')[pair['coordinate']['record_id']]
            source_context=a.read(Path(records[pair['coordinate']['record_id']]['prompt_json_path']))
            old_body=old_text.removeprefix(truth['random_string_to_prepend'])
            wrong_source_matches=[{'message_index':i,'role':z['role'],'content_sha256':a.digest(z['content'])}
                for i,z in enumerate(source_context) if z.get('content')==old_body]
            edits=[dict(operation=tag,old_bounds=[i,j],new_bounds=[k,l],
                old_codepoints=[ord(c) for c in old_text[i:j]] if j-i<=12 else None,
                new_codepoints=[ord(c) for c in new_text[k:l]] if l-k<=12 else None)
                for tag,i,j,k,l in SequenceMatcher(None,old_text,new_text).get_opcodes() if tag!='equal']
            turns=[]
            for index,(before,after) in enumerate(zip(on,nn,strict=True)):
                bt=before['response']['tokens'];at=after['response']['tokens']
                turns.append(dict(position=index,prompt_ids_equal=bt['prompt_ids']==at['prompt_ids'],
                    action_ids_equal=bt['completion_ids']==at['completion_ids'],
                    old_action_tokens=len(bt['completion_ids']),new_action_tokens=len(at['completion_ids']),
                    old_finish_reason=before['response']['finish_reason'],new_finish_reason=after['response']['finish_reason'],
                    old_native_content_sha256=a.digest(before['response']['message']['content']),
                    new_native_content_sha256=a.digest(after['response']['message']['content']),
                    old_action_ids_sha256=a.digest(bt['completion_ids']),new_action_ids_sha256=a.digest(at['completion_ids'])))
            rows.append(dict(phase=phase,coordinate=pair['coordinate'],win=pair['win'],loss=pair['loss'],
                old_exact=left['raw_exact'],new_exact=right['raw_exact'],old_chars=len(old_text),new_chars=len(new_text),gold_chars=len(gold),
                old_score=left['official_score'],new_score=right['official_score'],
                old_copy_type=left['copy_type'],new_copy_type=right['copy_type'],
                old_reply_sha256=a.digest(old_text),new_reply_sha256=a.digest(new_text),gold_sha256=a.digest(gold),
                programs_equal=pair['programs_equal'],observations_equal=pair['observations_equal'],
                old_clean_target_observed=left['mechanism']['clean_target_observed'],new_clean_target_observed=right['mechanism']['clean_target_observed'],
                old_context_message_exact_matches=wrong_source_matches,edits=edits,turns=turns,
                completion_token_change=right['cost']['root']['completion_tokens']-left['cost']['root']['completion_tokens'],
                old_episode=left['episode_path'],new_episode=right['episode_path']))
            private.append(dict(coordinate=pair['coordinate'],old_returned=old_text,new_returned=new_text,gold=gold))
    private_path=a.ROOT/'CHANGED_FINAL_TEXTS.private.json'
    with os.fdopen(os.open(private_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(private,f,indent=2,ensure_ascii=False);f.write('\n')
    import torch
    torch.set_num_threads(2)
    directory=s.train.OUTPUT/'gradient';g=torch.load(directory/'gradients.pt',map_location='cpu',weights_only=True)
    component=torch.load(directory/'negative-component-gradients.pt',map_location='cpu',weights_only=True)
    white=component['whitespace'];squared=lambda values:math.fsum(float(v.double().square().sum()) for v in values)
    total_norm=math.sqrt(squared(g.values()));white_norm=math.sqrt(squared(white.values()))
    residual={n:v-white.get(n,torch.zeros_like(v)) for n,v in g.items()}
    dot=math.fsum(float((g[n].double()*v.double()).sum()) for n,v in white.items())
    gradient=dict(total_norm=total_norm,negative_whitespace_norm=white_norm,
        total_vs_negative_whitespace_cosine=dot/(total_norm*white_norm),
        total_without_negative_whitespace_norm=math.sqrt(squared(residual.values())),
        actual_global_clipping_inactive=total_norm<1,
        interpretation='Vector diagnostic only; Adam normalization makes norm fraction an invalid parameter-update attribution.')
    value=dict(source_readout_sha256=a.sha(source),changed_token_paths=rows,first_prompt_and_action_arrays_equal=first_equal,
        paired_episodes=count,all_programs_equal=48,all_observations_equal=48,
        private_exact_final_receipt=str(private_path),private_exact_final_receipt_sha256=a.sha(private_path),
        gradient_diagnostic=gradient,source_sha256=dict(a.PINS),GPU_calls=0,generated_code_executed=False)
    a.write(a.ROOT/'CHANGED_OUTPUTS.json',value)
    print({'changed_paths':len(rows),'first_arrays_equal':first_equal,'gradient':gradient})

if __name__=='__main__':run()
