"""Additive identifier/collision receipt; never changes allocation or source artifacts."""
import ct_study as s

def collect(value,key):
    out=set()
    if isinstance(value,dict):
        for k,v in value.items():
            if k==key and type(v) in (int,str):out.add(v)
            elif isinstance(v,(dict,list)):out.update(collect(v,key))
    elif isinstance(value,list):
        for v in value:out.update(collect(v,key))
    return out
def main():
    contexts=s.read(s.ROOT/'inputs/PUBLIC.json');public_ids=[r['id'] for c in contexts for r in c['records']];context_ids=[c['native_context_id'] for c in contexts]
    receipt=s.read(s.ROOT/'inputs/PROVENANCE.json');paths=set(receipt['seed_inventory_sha256'])|{r['path'] for r in receipt['named_manifest_rows']}
    old_ids=set();old_contexts=set();pins={}
    for path in sorted(paths):
        value=s.read(path);old_ids.update(collect(value,'id'));old_contexts.update(collect(value,'native_context_id'));old_contexts.update(collect(value,'context_window_id'));pins[path]=s.sha(path)
    record_overlap=set(public_ids)&old_ids;context_overlap=set(context_ids)&old_contexts
    if len(set(public_ids))!=128 or len(set(context_ids))!=8 or record_overlap or context_overlap:raise ValueError('collision qualification failed; no reranking')
    result=dict(public_ids=public_ids,native_context_ids=context_ids,unique_public_ids=128,unique_native_context_ids=8,record_id_collisions=sorted(record_overlap),native_context_id_collisions=sorted(context_overlap),named_existing_ids=len(old_ids),named_existing_native_ids=len(old_contexts),source_sha256=pins,scope='exact named refreshed root PUBLIC/GROUPS/TASKS and all sidecar input PLAN seed manifests; not global namespace guarantee',allocation_unchanged=True)
    s.write(s.ROOT/'CPU_COLLISION_RECEIPT.json',result);print({k:v for k,v in result.items() if k not in ('source_sha256','public_ids','native_context_ids')})
if __name__=='__main__':main()
