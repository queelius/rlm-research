"""Bind all original flat18 actions and freeze nine new metadata-only held stages."""
import json
import os
from pathlib import Path
import study as s

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (s.ROOT/'DATA_RECEIPT.json').exists()
    assert s.sha(s.WIDTH/'READY_RUN.json')=='117837ff4d26f93b533f9cf15a589ebbe6514fb3d75aa2dcd9f0b1a2dde22a81'
    audit=s.read(s.REVIEW/'readout-001.json');assert audit['status']=='COMPLETE' and not audit['issues']
    assert s.sha(s.REVIEW/'readout-001.json')=='1fd4008bebab107b0224f8c5ddf2d6fa1c92e1e4dabd33c526b0064da6b4329b'
    width=s.width;target=width.gold();episodes=[];evaltasks=[];pins={}
    for c in [c for c in width.calls() if c['helpers']==1]:
        cid=width.call_id(c);path=width.ATTEMPT/'calls'/f'{cid}.json';record=s.read(path)
        body=s.read(record['request_path']);response=s.read(record['response_path'])
        assert body==width.request_body(width.prompt(c),c['seed'],384)
        decoded=width.decode_response(body,response);assert decoded['transport_valid']
        assert decoded['completion_ids']==record['completion_ids'] and decoded['text']==record['text']
        known={r['implementation_id'] for r in width.child(c)['stage']['tables']['implementations']}
        predicted=json.loads(decoded['text'])['eligible_ids'];assert len(predicted)==len(set(predicted)) and set(predicted)<=known
        action=decoded['completion_ids'];prompt=body['token_ids'];mask,receipt=s.array_mask(action,width.tokenizer())
        turn=dict(prompt_ids=prompt,action_ids=action,input_ids=prompt+action,old_logprobs=decoded['completion_logprobs'],
                  labels=[-100]*len(prompt)+action,loss_mask=[0]*len(prompt)+[1]*len(action))
        episodes.append(dict(episode_id=cid,group_id=c['root_id'],available=True,call=c,
            reward=s.reward(set(predicted),set(target[c['root_id']]),known),predicted_ids=predicted,
            known_ids=sorted(known),gold_ids=target[c['root_id']],root_turns=[turn],
            selection_mask=mask,actual_loss_mask=[0]*len(prompt)+mask,mask_receipt=receipt,
            source_record=str(path),source_response_raw_sha256=s.sha(record['response_path']),
            source_response_canonical_sha256=decoded['response_sha256']))
        for p in (path,Path(record['request_path']),Path(record['response_path']),Path(record['prompt_path'])):pins[str(p)]=s.sha(p)
        evaltasks.append(dict(split='train',root_id=c['root_id'],width=c['width'],repeat=c['alternative'],
            seed=c['seed'],prompt=width.prompt(c),request=body,known_ids=sorted(known)))
    for r in episodes:
        other=next(x for x in episodes if x['group_id']==r['group_id'] and x['episode_id']!=r['episode_id'])
        r.update(baseline=other['reward'],advantage=r['reward']-other['reward'])
    data=dict(schema='b05-flat18-native-array-RLOO-v1',episodes=episodes,denominator=18,
        source_pins=pins,native_call_reuse=True,all_flat_replies_retained=True,no_cp32_weights=True)
    s.validate_inputs(data)
    if s.INPUTS.exists():assert s.read(s.INPUTS)==data, 'partial training inventory changed'
    else:s.write_x(s.INPUTS,data)
    s.INPUTS.chmod(0o600)
    with s.aliases({'study':width},s.WIDTH):
        interface=s.load('selection_width_ID_contract',s.WIDTH/'interface.py')
    api=width.source.b05();old=s.read(width.SOURCE/'inputs/PUBLIC.json')['roots']
    usedroots={r['safe_root']['root_id'] for r in old+width.active_roots()}
    usedids={r['implementation_id'] for x in old+width.active_roots() for stage in x['safe_root']['stages'] for r in stage['tables']['implementations']}
    held=[];goldrows=[]
    for wi,n in enumerate((6,12,20)):
        for si in range(3):
            seed=202609320000+100*wi+si
            root=api.generate(seed,api.StructuralConfig(n,1,1,3,1,'chain','helper-width-local-v1'))
            assert root['root_id'] not in usedroots;usedroots.add(root['root_id'])
            allids={r['implementation_id'] for stage in root['stages'] for r in stage['tables']['implementations']}
            assert not allids&usedids;usedids|=allids
            child=api.extract_child(root,si);gold=api.solve_child_reference(child)
            assert gold==api.solve_child_independent(child)
            prompt=interface.render(api.render_child(child))
            known=sorted(r['implementation_id'] for r in child['stage']['tables']['implementations'])
            held.append(dict(root_id=root['root_id'],seed=seed,width=n,selected_stage=si,
                safe_root=api.build_safe_root_record(root),prompt=prompt,known_ids=known))
            goldrows.append(dict(split='held',root_id=root['root_id'],gold_ids=[r['implementation_id'] for r in gold['rows']]))
            for rep in range(2):
                sample=202609330000+2*(3*wi+si)+rep;body=width.request_body(prompt,sample,384)
                assert len(body['token_ids'])+384<=8192
                assert len(width.tokenizer().encode(width.canonical_json({'eligible_ids':known}),add_special_tokens=False))+1<=384
                evaltasks.append(dict(split='held',root_id=root['root_id'],width=n,repeat=rep,seed=sample,prompt=prompt,request=body,known_ids=known))
    goldrows+=[dict(split='train',root_id=k,gold_ids=v) for k,v in target.items()]
    s.write_x(s.ROOT/'HELD_PUBLIC.json',dict(roots=held,outcome_blind=True,model_queries=0,original17roots_and_allIDs_disjoint=True))
    s.write_x(s.ROOT/'HOST_GOLD.json',dict(rows=goldrows));(s.ROOT/'HOST_GOLD.json').chmod(0o600)
    s.write_x(s.ROOT/'EVAL_TASKS.json',dict(tasks=evaltasks,planned_per_model=36,fresh_models=2,total72=True))
    s.write_x(s.ROOT/'DATA_RECEIPT.json',dict(train18=len(episodes),nonzero8=sum(r['advantage']!=0 for r in episodes),
        held_stages9=len(held),eval_tasks36=len(evaltasks),max_actual_context=max(len(t['request']['token_ids'])+384 for t in evaltasks),
        selected_loss_tokens_nonzero=sum(sum(r['selection_mask']) for r in episodes if r['advantage']!=0),
        token_boundary_overlaps=[dict(episode_id=r['episode_id'],boundaries=r['mask_receipt']['boundary_overlap_tokens']) for r in episodes],
        source_outcome_SHA=s.sha(s.REVIEW/'readout-001.json'),no_models_queried=True,
        artifact_sha256={str(p):s.sha(p) for p in (s.INPUTS,s.ROOT/'HELD_PUBLIC.json',s.ROOT/'HOST_GOLD.json',s.ROOT/'EVAL_TASKS.json')}))
    print(json.dumps({k:v for k,v in s.read(s.ROOT/'DATA_RECEIPT.json').items() if k not in ('token_boundary_overlaps','artifact_sha256')}))

if __name__=='__main__':main()
