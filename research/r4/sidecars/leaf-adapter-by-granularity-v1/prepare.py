"""Identical fresh native batches, with adapter or original base selected."""
import copy
import bg_study as s
def build():
    old=s.read(s.PRIOR/'inputs/PLAN.json');requests=s.read(s.PRIOR/'inputs/REQUESTS.json')
    rows=[];bodies={}
    for original in old:
        order=('base','c32') if (original['context_index']+original['repeat']+original['batch'])%2==0 else ('c32','base')
        for policy in order:
            row={**original,'model_policy':policy,'seed':s.SEEDS[original['repeat']],'dispatch_order':len(rows)}
            row['id']=s.digest(['leaf-adapter-by-granularity-v1',original['id'],policy,row['seed']])
            body=copy.deepcopy(requests[original['id']])
            if policy=='base':body['model']=s.BASE_MODEL
            body['sampling_params']['seed']=row['seed']
            assert len(body['token_ids'])+2048<=8192
            rows.append(row);bodies[row['id']]=body
    return rows,bodies
def main():
    import time
    started=time.time();rows,bodies=build()
    assert len(rows)==152
    from prime_rl.configs.inference import InferenceConfig
    # Body shape and token IDs are inherited from the previously executed native
    # requests. Base is an already listed service model; no changed token renderer.
    for name in ('PUBLIC.json','HOST_GOLD.json'):
        s.write(s.ROOT/'inputs'/name,s.read(s.PRIOR/'inputs'/name))
    s.write(s.ROOT/'inputs/PLAN.json',rows);s.write(s.ROOT/'inputs/REQUESTS.json',bodies)
    source=[s.PRIOR/'READY.json',s.PRIOR/'inputs/PLAN.json',s.PRIOR/'inputs/REQUESTS.json',
            s.PRIOR/'inputs/PUBLIC.json',s.PRIOR/'inputs/HOST_GOLD.json']
    s.write(s.ROOT/'inputs/PROVENANCE.json',dict(source_sha256={str(p):s.sha(p) for p in source},
        selection='same two exposed contexts; no outcome reranking',fresh_both_models=True,seeds=list(s.SEEDS)))
    old=s.read(s.PRIOR/'outputs/attempt-001/owned-service/SUITE_PREFLIGHT.json')['models']['data']
    expected={s.BASE_MODEL,s.binding()['fixed_child']}
    assert expected.issubset({r['id'] for r in old})
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(planned=152,max_prefix=max(len(x['token_ids']) for x in bodies.values()),
        same_native_prefix_within_model_pair=True,base_and_child_previously_listed=sorted(expected),
        typed_sampling_and_schema_unchanged=True,elapsed_seconds=time.time()-started,gpu_calls=0))
    print(dict(planned=152,max_prefix=max(len(x['token_ids']) for x in bodies.values())))
if __name__=='__main__':main()
