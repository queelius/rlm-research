"""Host-only raw source oracle and measured actual-child-template budget; no model calls."""
import argparse
import json
from pathlib import Path
import ss_study as s

def main(fixture):
    receipt=s.ROOT/'CPU_SOURCE_CHILD.json'
    if receipt.exists():raise FileExistsError('qualification receipt preserved')
    contexts=s.read(s.ROOT/'inputs/PUBLIC.json');parents=s.read(s.ROOT/'inputs/PARENTS.json');plans=s.read(s.ROOT/'inputs/FREE_PLAN.json');gold=s.read(s.ROOT/'inputs/HOST_GOLD.json')
    source=s.SIDE/'trec-leaf-sft-v1/source/data.py';module=s.load('scale_independent_raw_rows',source,'b5aa353e2173c3fd48ecc36ce0596c9c3328767a7d82c8d22c57b4e0a32f0b8f')
    raw={r['group_id']:r for r in module.load_partitions()['train']};mapped={}
    for parent in parents:
        context=next(c for c in contexts if c['parent_id']==parent['id'] and c['size']==256)
        for record,gid,pin in zip(context['records'],parent['group_ids'],parent['source_rows'],strict=True):
            original=raw[gid];assert record['text']==original['question'] and pin['source_line_1based']==original['source_line_1based'] and pin['source_path']==original['source_path']
            assert gold[context['id']]['labels'][record['id']]==original['gold'];mapped[record['id']]=original['gold']
    truths=[]
    for row in plans:
        context=next(c for c in contexts if c['id']==row['context_id']);total=0
        for record in context['records']:
            if mapped[record['id']]==row['target']:total+=1 if row['operator']=='count' else record['weight']
        assert total==gold[context['id']]['answers'][row['family']];truths.append(dict(id=row['id'],gold=total))
    helper_path=s.SIDE/'adaptive-filter-pilot-v1/batch_contract.py';helper=s.load('scale_measured_helper',helper_path,'d2c7f8df62a4190930dbf3e14f7e68cfb27cc573898bbc343117e8d97190bd88')
    call=s.read(fixture);body=call['body'];assert body['model']==s.binding()['fixed_child'] and body['sampling_params']['max_tokens']==2048
    tokenizer=s.stack().native.renderer()._tokenizer;text=tokenizer.decode(body['token_ids']);assert tokenizer.encode(text,add_special_tokens=False)==body['token_ids']
    requested=body['sampling_params']['structured_outputs']['json']['required'];context=next(c for c in contexts if set(requested)<=set(r['id'] for r in c['records']))
    original=helper.request_for([r for r in context['records'] if r['id'] in requested]);assert text.count(original)==1
    budgets=[]
    for context in contexts:
        prompt=text.replace(original,helper.request_for(context['records']));n=len(tokenizer.encode(prompt,add_special_tokens=False))
        maps={label:len(tokenizer.encode(json.dumps({r['id']:label for r in context['records']},ensure_ascii=False,separators=(',',':')),add_special_tokens=False)) for label in helper.LABELS}
        budgets.append(dict(context=context['id'],records=context['size'],child_input_tokens=n,plus_max2048=n+2048,input_fits8192=n<=8192,requested_input_output_fits8192=n+2048<=8192,constant_map_output_tokens=maps))
    assert len(mapped)==1024 and len(truths)==24 and len(budgets)==12
    s.write(receipt,dict(source_sha256={str(source):s.sha(source),str(helper_path):s.sha(helper_path),str(fixture):s.sha(fixture)},actual_child_template_from_authored_fixture=True,template_roundtrip_exact=True,context_tokens=8192,child_action_tokens=2048,rows_verified=1024,truths=truths,budgets=budgets,model_calls=0,selection_unchanged=True,interpretation='Full typed-map route pressure only, not every possible one-call strategy. Constant maps are illustrative serializations, never sampled/gold targets.'))
    print(dict(raw_rows=1024,truths=24,child_budgets=12,sha256=s.sha(receipt)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('fixture',type=Path);main(p.parse_args().fixture)
