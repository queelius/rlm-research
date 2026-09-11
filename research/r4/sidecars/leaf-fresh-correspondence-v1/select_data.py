"""Frozen membership crosswalk and exact raw source selection; no outcomes."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import json
import pyarrow.parquet as pq
import study as s


def prepare():
    s.check(s.FEAS/'FINAL_COUNTS.json','2400d2b7f82d4dbbc63ffd92e0be4c05b164362dec45ae0122458580bd34b470')
    s.check(s.FEAS/'FINAL_SOURCE_HASHES.json','16ade16427223fbe5cc99783766ed28fbf0187af4dad4452a03a767822c1e85e')
    evidence=s.read(s.FEAS/'FINAL_COUNTS.json');pins=s.read(s.FEAS/'FINAL_SOURCE_HASHES.json')
    excluded=set();matched_catalogs=[];source={str(s.FEAS/name):s.sha(s.FEAS/name) for name in ('REPORT.md','FINAL_COUNTS.json','FINAL_SOURCE_HASHES.json','FINAL_MANIFEST.json')}
    cache=Path('/project/alex_phd/research-cache/datasets')
    datasets={'agnews':(cache/'fancyzhx--ag_news--eb185aade064a813bc0b7f42de02595523103ca4/test.parquet','text',['World','Sports','Business','Sci/Tech']),
      'sst2':(cache/'sst2-train-feasibility-20260909/train.parquet','sentence',['negative','positive'])}
    pools={};universe=set()
    for task,(path,column,labels) in datasets.items():
        s.check(path,pins[str(path)]);source[str(path)]=pins[str(path)]
        pools[task]=[{'index':i,'text':row[column],'label':row['label']} for i,row in enumerate(pq.read_table(path).to_pylist())]
        universe.update(s.group(r['text']) for r in pools[task])
    def visit(value,found):
        if isinstance(value,dict):
            for key,item in value.items():
                if key in ('dedup','acquisition','source_sha256','source_provenance','freshness') or 'provenance' in key:continue
                if key in ('question','text','sentence') and isinstance(item,str) and s.group(item) in universe:found.add(s.group(item))
                visit(item,found)
        elif isinstance(value,list):
            for item in value:visit(item,found)
        elif isinstance(value,str) and value in universe:found.add(value)
    for catalog in evidence['input_inventory']:
        path=Path(catalog['path']);s.check(path,catalog['sha256']);source[str(path)]=catalog['sha256']
        found=set();visit(s.read(path),found);excluded.update(found)
        matched_catalogs.append({'path':str(path),'sha256':catalog['sha256'],'matching_groups_for_new_pools':len(found)})
    templates=s.read(s.OLD/'DATA.json')['contexts'];contexts=[];audits={}
    for task,(path,column,labels) in datasets.items():
        rows,audit=s.choose(pools[task],excluded,task);audits[task]=audit
        expected=evidence['pools']['ag_test' if task=='agnews' else 'sst_train']
        if len(audit['excluded_groups'])!=expected['matched_declared_input_or_reservation_groups'] or audit['eligible_groups']!=expected['available_after_bounded_scan']:raise ValueError('frozen membership counts disagree')
        template=next(c for c in templates if c['dataset']==task)
        for ci in range(4):
            selected=rows[ci*64:(ci+1)*64]
            numbers=sorted(range(1000,10000),key=lambda n:s.digest([s.MASTER,task,ci,'source-id',n]))[:64]
            records=[]
            for position,(row,number) in enumerate(zip(selected,numbers),1):
                records.append({'source_row_index':row['index'],'source_row_indexes':row['source_row_indexes'],
                  'source_file':str(path),'source_split':'test' if task=='agnews' else 'train','question':row['text'],
                  'source_label':row['label'],'group_id':row['group_id'],'gold_label':labels[row['label']],
                  'id':f'q{number:04d}','source_position':position,'input_position':position,'source_rank':position,'selection_hash':row['selection_hash']})
            body=deepcopy(template['base_request']);prefix=body['messages'][1]['content'].split(s.INPUT_MARKER)[0]
            if task=='sst2':
                if prefix.count('movie-review sentence')!=1:raise ValueError('SST wording seam')
                prefix=prefix.replace('movie-review sentence','movie-review text unit')
            body['messages'][1]['content']=prefix+s.INPUT_MARKER+json.dumps({r['id']:r['question'] for r in records},ensure_ascii=False)
            contexts.append({'index':len(contexts),'dataset':task,'source_context_index':ci,'source_context_id':f'fresh-{task}-{ci:02d}',
              'source_spec_path':str(s.FEAS/'FINAL_COUNTS.json'),'source_spec_sha256':s.sha(s.FEAS/'FINAL_COUNTS.json'),
              'records':records,'labels':labels,'base_request':body})
        audit['selected_label_counts']=dict(Counter(r['label'] for r in rows))
        audit['selected_word_counts']=dict(Counter(min(10,len(r['text'].split())) for r in rows))
    # Acquisition/card bytes are retained, without elevating software licenses to dataset licenses.
    for name,h in pins.items():
        if Path(name).name in ('ACQUISITION.json','README.md'):
            s.check(name,h);source[name]=h
    data={'contexts':contexts,'master_seed':s.MASTER,'sampling_seeds':s.SEEDS,
      'exposure':'fresh exact groups relative to frozen named catalogs; SST train phrases/text units; near-duplicates and model pretraining unresolved',
      'source_provenance':{'source_sha256':source,'catalogs':matched_catalogs,'selection':audits,'underlying_dataset_license':'unknown/unconfirmed',
      'selection_rule':'SHA256(master:task:selection:normalized_group); first256; four contiguous64; earliest raw row; IDs independent of labels'}}
    s.write_once(s.ROOT/'DATA.json',data);s.write_once(s.ROOT/'SELECTION_PROVENANCE.json',data['source_provenance'])
    print(s.serialize({'selected':512,'contexts':8,'pools':{k:{'eligible':v['eligible_groups'],'excluded':len(v['excluded_groups']),'conflicts':len(v['conflict_groups'])} for k,v in audits.items()}}),flush=True)


if __name__=='__main__':prepare()
