"""Label-blind public source selection and timestamped bounded exclusion receipt."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import random
import re
import time
import protocol as p
import study as s

CACHE=Path('/project/alex_phd/research-cache/datasets/multinli-correspondence-feasibility-20260909-da70db2')
PARQUET=CACHE/'validation_matched.parquet'
PARQUET_SHA='350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186'


def text_group(text):return hashlib.sha256(p.normalize(text).encode()).hexdigest()


def exposure(rows):
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    universe={text_group(r[k]) for r in rows for k in ('premise','hypothesis')};hits=set();catalogs=[];skipped=[]
    def visit(value,found):
        if isinstance(value,dict):
            for key,item in value.items():
                if key in ('dedup','acquisition','source_sha256','source_provenance','freshness') or 'provenance' in key:continue
                if key in ('question','text','sentence','premise','hypothesis') and isinstance(item,str):
                    h=text_group(item)
                    if h in universe:found.add(h)
                visit(item,found)
        elif isinstance(value,list):
            for item in value:visit(item,found)
        elif isinstance(value,str) and value in universe:found.add(value)
    prune={'outputs','output','qualification','qualifications','tests','test','analyses','research-cache','checkpoints',
           '.git','.venv','venv','__pycache__','service','source','src','node_modules','probe-outputs','exports','training'}
    for base,dirs,files in os.walk('/project/alex_phd/runs'):
        dirs[:]=[d for d in dirs if d not in prune and not d.startswith(('attempt','service-','qualification-')) and Path(base)/d!=s.ROOT]
        for name in files:
            if not re.fullmatch(r'(?:DATA|PUBLIC(?:_CATALOGS)?|GROUPS|SPEC(?:[-_.][\w.-]+)?|CONTEXTS|RESERVATIONS|INPUTS|WORLDS|PACKAGES)\.json',name):continue
            path=Path(base)/name
            if path.stat().st_size>32_000_000:skipped.append(str(path));continue
            raw=path.read_bytes()
            try:value=json.loads(raw)
            except ValueError:skipped.append(str(path));continue
            found=set();visit(value,found);hits.update(found)
            catalogs.append(dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),hits=len(found)))
    return hits,dict(started_utc=started,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),catalogs=catalogs,
        skipped=skipped,exact_text_hits=sorted(hits),scope='Named-input exact text crosswalk; no arbitrary embedded prompt/near-duplicate/pretraining guarantee')


def select(rows,excluded):
    pairs=collections.defaultdict(list)
    for index,row in enumerate(rows):pairs[p.pair_group(row)].append((index,row))
    premises=collections.defaultdict(list)
    conflicts=[]
    for h,values in pairs.items():
        if len({r['label'] for _,r in values})!=1:conflicts.append(h);continue
        index,row=min(values,key=lambda x:x[0])
        if row['label'] not in (0,1,2):continue
        premises[text_group(row['premise'])].append((h,index,row))
    eligible={h:values for h,values in premises.items() if len(values)==3 and h not in excluded
              and not any(text_group(r['hypothesis']) in excluded for _,_,r in values)
              and len({r['genre'] for _,_,r in values})==1}
    contexts=[];chosen=[]
    for genre in p.GENRES:
        ranked=sorted([h for h,values in eligible.items() if values[0][2]['genre']==genre],
                      key=lambda h:s.digest([p.MASTER,'select',genre,h]))
        if len(ranked)<32:raise ValueError('insufficient whole premise groups: '+genre)
        for gi in range(2):
            groups=ranked[gi*16:(gi+1)*16];chosen.extend(groups);records=[];ci=len(contexts)
            for round_index in range(3):
                ordered=sorted(groups,key=lambda h:s.digest([p.MASTER,'display',ci,round_index,h]))
                for h in ordered:
                    pair_h,index,row=sorted(eligible[h],key=lambda x:x[0])[round_index]
                    records.append(dict(id=p.public_id(row),premise=row['premise'],hypothesis=row['hypothesis'],
                        gold_label=p.LABELS[row['label']],pair_group=pair_h,premise_group=h,source_row=index,
                        original_pairID=row['pairID'],original_promptID=row['promptID']))
            contexts.append(dict(index=ci,genre=genre,premise_groups=groups,records=records))
    ids=[r['id'] for c in contexts for r in c['records']]
    if len(set(ids))!=384 or len(set(chosen))!=128:raise ValueError('public-ID collision or overlapping premises')
    return contexts,dict(pair_conflicts=conflicts,eligible_premises=len(eligible),selected_premise_groups=chosen,
        selected_pairs=384,selection_is_not_gold_balanced=True)


def public(contexts):return [dict(index=c['index'],records=[{k:r[k] for k in ('id','premise','hypothesis')} for r in c['records']]) for c in contexts]


def main():
    import pyarrow.parquet as pq
    started=time.time()
    if s.sha(PARQUET)!=PARQUET_SHA:raise ValueError('source parquet differs')
    rows=pq.read_table(PARQUET).to_pylist();excluded,receipt=exposure(rows)
    if receipt['skipped']:raise ValueError('source scan incomplete; review before selection')
    contexts,selection=select(rows,excluded)
    mutated=[{**r,'label':int(s.digest([p.MASTER,'arbitrary-gold-mutation',index]),16)%3} for index,r in enumerate(rows)]
    changed,_=select(mutated,excluded)
    if public(contexts)!=public(changed):raise ValueError('public selection depends on gold labels')
    ids=[r['id'] for c in contexts for r in c['records']]
    constant,tokens=p.choose_constant(ids,s.tokenizer());plan=p.plan(contexts)
    for name,value in {'DATA.json':dict(contexts=contexts,constant=constant), 'PUBLIC.json':public(contexts),
        'PLAN.json':plan,'CONTROL_TAG_TOKENS.json':tokens,'EXPOSURE.json':receipt,
        'SELECTION.json':selection,'PLANNED_NULL_ENDPOINTS.json':[p.null_row(r,'frozen before startup') for r in plan]}.items():s.write(s.ROOT/name,value)
    s.write(s.ROOT/'SOURCE_MANIFEST.json',dict(source=str(PARQUET),source_sha256=PARQUET_SHA,
        acquisition=str(CACHE/'ACQUISITION.json'),acquisition_sha256=s.sha(CACHE/'ACQUISITION.json'),
        card_sha256=s.sha(CACHE/'README.md'),revision='da70db2af9d09693783c3320c4249840212ee221',split='validation_matched',
        license='Nonfiction OANC source terms; original mixed license card retained; not blanket MIT',
        original_source_receipt='/project/alex_phd/runs/rlm-research-r4/analyses/multinli-correspondence-feasibility-2026-09-09/SOURCE_FEASIBILITY.json',
        public_label_mutation_invariant=True,host_prepare_seconds=time.time()-started,
        tag_source='normalized public text only; original source IDs stay host-side',gpu_calls=0,model_calls=0))
    print(dict(contexts=8,pairs=384,premises=128,plan=len(plan),constant=constant,
        target=tokens['modal_target'],actual=tokens['chosen']['tokens'],residual=tokens['residual_control_minus_matching'],catalogs=len(receipt['catalogs'])))


if __name__=='__main__':main()
