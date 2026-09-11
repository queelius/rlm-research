"""Qualified six full72 updates; explicit504 mapping and approved validity/cost gate."""
import functools
import math
import qs_study as s
import qs_learning as l
@functools.lru_cache(maxsize=1)
def implementation():
    path=s.OLD/'od_train.py';m=s.load('qs_qualified_six_update_trainer',path,s.cf_ready['source_sha256'][str(path)],{'od_study':s,'od_learning':l});m.SEED=s.SEED
    m._qualified_load_model=m.load_model;original_gate=m.gate
    def load_model(output):
        model,params,helper=m._qualified_load_model(output);named=[(n,p) for n,p in model.named_parameters() if p.requires_grad]
        if len(params)!=504 or len(named)!=504 or [id(p) for n,p in named]!=[id(p) for p in params]:raise ValueError('exact504 named trainable parameter mapping')
        s.write(output/'PARAMETER_MAPPING.json',dict(parameters=[dict(index=i,name=n,shape=list(p.shape)) for i,(n,p) in enumerate(named)],optimizer_origin='fresh Adam at0',starting=s.starting_policy(),child_loaded=False))
        return model,params,helper
    def gate(model,episodes,deadline):
        import torch
        torch.cuda.reset_peak_memory_stats();result=original_gate(model,episodes,deadline)
        for row in result['rows']:
            for role in row['roles']:
                if not math.isfinite(role['target_nll']) or (role['kind']!='terminal' and not math.isfinite(role['mechanism_nll'])):raise ValueError('finite actual role/nonliteral NLL required')
        result.update(gate_policy='MAIN-approved validity/cost only; no fit threshold',peak_memory_allocated=torch.cuda.max_memory_allocated(),peak_memory_reserved=torch.cuda.max_memory_reserved(),memory_admission='actual forward execution without OOM; measured bytes, no synthetic CPU timing claim')
        return result
    m.load_model=load_model;m.gate=gate;return m
def main():
    m=implementation();m.run(m.parse_args())
if __name__=='__main__':main()
