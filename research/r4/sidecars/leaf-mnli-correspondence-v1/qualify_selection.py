"""Independent per-row valid-label mutation and exact raw shared-premise checks."""
import collections
import pyarrow.parquet as pq
import protocol as p
import select_data as d
import study as s


def main():
    if s.sha(d.PARQUET)!=d.PARQUET_SHA:raise ValueError('source changed')
    rows=pq.read_table(d.PARQUET).to_pylist();excluded=set(s.read(s.ROOT/'EXPOSURE.json')['exact_text_hits'])
    original=s.read(s.ROOT/'DATA.json')['contexts'];selected,_=d.select(rows,excluded)
    if original!=selected:raise ValueError('original source selection changed')
    changed=[{**r,'label':int(s.digest([p.MASTER,'arbitrary-gold-mutation',i]),16)%3} for i,r in enumerate(rows)]
    mutated,_=d.select(changed,excluded)
    if d.public(original)!=d.public(mutated):raise ValueError('per-row label mutation changed public selection')
    groups=collections.defaultdict(list)
    for ctx in original:
        for r in ctx['records']:groups[r['premise_group']].append(r)
    proof={h:dict(raw_premise_variants=len({r['premise'] for r in values}),
        raw_premise_sha256=sorted({s.digest(r['premise']) for r in values}),pair_count=len(values),
        source_rows=sorted(r['source_row'] for r in values)) for h,values in groups.items()}
    result=dict(passed=True,per_row_arbitrary_valid_label_mutation_public_invariant=True,
        mutation_rule='int(sha256(canonical [master, arbitrary-gold-mutation, source-row-index]),16)%3',
        source_pairs_unique=len({p.pair_group(r) for r in rows})==len(rows),
        selected_premises=len(groups),all_selected_raw_premises_identical=all(v['raw_premise_variants']==1 for v in proof.values()),
        selected_group_raw_premise_proof=proof,source_sha256={str(d.PARQUET):d.PARQUET_SHA,
            **{str(s.ROOT/name):s.sha(s.ROOT/name) for name in ('qualify_selection.py','select_data.py','protocol.py','DATA.json','EXPOSURE.json')}},
        no_source_replacement=True,gpu_calls=0,model_calls=0)
    s.write(s.ROOT/'SELECTION_QUALIFICATION.json',result)
    print({k:v for k,v in result.items() if k not in ('selected_group_raw_premise_proof','source_sha256')})


if __name__=='__main__':main()
