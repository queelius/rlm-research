"""Deterministic public-only native requests, original wide prefix roundtrip."""
import copy
import json
import bg_study as s
import bg_protocol as p
def requests(contexts,templates,tokenizer):
    plan=[];bodies={};checks=[]
    for repeat,seed in enumerate(s.SEEDS):
        for ci,ctx in enumerate(contexts):
            original=templates[ci];first=original[0]['body'];text=tokenizer.decode(first['token_ids']);offset=text.rindex('Records: ')+len('Records: ')
            _,length=json.JSONDecoder().raw_decode(text[offset:]);prefix,suffix=text[:offset],text[offset+length:]
            arms=('W','S') if (ci+repeat)%2==0 else ('S','W')
            for arm in arms:
                for bi,batch in enumerate(p.partitions(ctx['records'],arm)):
                    public=[{'id':r['id'],'text':r['text']} for r in batch];body=copy.deepcopy(first)
                    body['token_ids']=tokenizer.encode(prefix+json.dumps(public,separators=(',',':'),ensure_ascii=False)+suffix,add_special_tokens=False)
                    ids=[r['id'] for r in batch];base_schema=body['sampling_params']['structured_outputs']['json'];example=next(iter(base_schema['properties'].values()))
                    base_schema['properties']={k:copy.deepcopy(example) for k in sorted(ids)};base_schema['required']=ids
                    if arm=='W':
                        expected=copy.deepcopy(original[bi]['body']);expected['sampling_params']['seed']=seed
                        body['sampling_params']['seed']=seed
                        if body!=expected:raise ValueError('historical native wide prompt/schema reconstruction differs')
                    body['sampling_params']['seed']=seed
                    if len(body['token_ids'])+2048>8192:raise ValueError('fixed native context admission')
                    coordinate=dict(context_index=ci,context_id=ctx['id'],repeat=repeat,seed=seed,arm=arm,batch=bi+1,ids=ids,n=len(ids))
                    coordinate['id']=s.digest(['c32-batch-granularity-v1',ci,repeat,arm,bi]);plan.append(coordinate);bodies[coordinate['id']]=body
                    checks.append(dict(id=coordinate['id'],input_tokens=len(body['token_ids']),wide_original_exact=arm=='W'))
    return plan,bodies,checks
def main():
    diag=s.read(s.DIAG/'RECONSTRUCTION.json');contexts=[];templates=[];pins={str(s.DIAG/'READY.json'):s.sha(s.DIAG/'READY.json')}
    source={r['id']:r for r in s.read(s.BV/'inputs/PUBLIC.json')};gold=s.read(s.BV/'inputs/HOST_GOLD.json');selected_gold={}
    for row in diag['endpoints']:
        c=row['coordinate'];contexts.append(source[c['context_id']]);selected_gold[c['context_id']]=gold[c['context_id']]
        original=[]
        for batch in row['batches']:
            path=batch['path'];pins[path]=s.sha(path);original.append(dict(path=path,body=s.read(path)['body']))
        templates.append(original)
    for path in [s.BV/'inputs/PUBLIC.json',s.BV/'inputs/HOST_GOLD.json',s.DIAG/'RECONSTRUCTION.json']:pins[str(path)]=s.sha(path)
    _,tokenizer=s.renderer();plan,bodies,checks=requests(contexts,templates,tokenizer)
    assert len(plan)==76 and len(contexts)==2 and sum(len(c['records']) for c in contexts)==512
    s.write(s.ROOT/'inputs/PUBLIC.json',contexts);s.write(s.ROOT/'inputs/HOST_GOLD.json',selected_gold);s.write(s.ROOT/'inputs/TEMPLATES.json',templates)
    s.write(s.ROOT/'inputs/PLAN.json',plan);s.write(s.ROOT/'inputs/REQUESTS.json',bodies)
    s.write(s.ROOT/'inputs/PROVENANCE.json',dict(source_sha256=pins,assigned_rows=[20,30],selection='purposive after bounded multi-batch child-label failures',fresh_both_arms=True,seed_namespace=list(s.SEEDS),seed_scan='rg 98690170[12] over prepared sidecar JSON/Python excluding outputs/qualification, before declaration: exit1 no matches',no_source_reselection=True))
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(checks=checks,max_prefix=max(x['input_tokens'] for x in checks),all_prefixes_fit=True,wide_native_exact=sum(x['wide_original_exact'] for x in checks),source_private_fields_in_request=False))
    print(dict(planned=len(plan),max_prefix=max(x['input_tokens'] for x in checks),wide_exact=12))
if __name__=='__main__':main()
