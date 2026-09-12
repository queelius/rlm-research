"""Outcome-blind CPU-only selection; all answers and annotations remain host-only."""
from collections import Counter
import hashlib
import json
import os
import zipfile
import musique_study as s


def main():
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU preparation only')
    if s.INPUTS.exists():raise FileExistsError('immutable inputs already exist')
    expected='2ced9a11afde1e017e4cb62a5d3dd9d616ee65e2f2ab8bdb46ba90fc140065b7'
    if s.sha(s.FEASIBILITY/'FEASIBILITY_READY.json')!=expected:raise ValueError('feasibility identity changed')
    ready=s.read(s.FEASIBILITY/'FEASIBILITY_READY.json')
    for path,value in ready['closure_sha256'].items():
        if s.sha(path)!=value:raise ValueError('feasibility closure changed: '+path)
    inventory={r['id']:r for r in s.read(s.FEASIBILITY/'CANDIDATE_INVENTORY.json')}
    with zipfile.ZipFile(s.ARCHIVE) as archive:
        raw_rows=[(json.loads(raw),raw) for raw in archive.open('data/musique_ans_v1.0_dev.jsonl')]
    ranked=sorted(raw_rows,key=lambda pair:hashlib.sha256((s.NAMESPACE+'|'+s.digest(pair[0])).encode()).hexdigest())
    counts=Counter(); seen_questions=set(); seen_steps=set(); seen_supports=set(); selected=[]; gold={}; skipped=Counter()
    for row,raw in ranked:
        item=inventory[row['id']];hop=item['hop_count']
        if counts[hop]>=4:continue
        if item['public_qwen_tokens']>5500:skipped['public_token_bound']+=1;continue
        question=' '.join(row['question'].lower().split())
        if question in seen_questions or seen_steps.intersection(item['singlehop_ids']) or seen_supports.intersection(item['support_paragraph_sha256']):
            skipped['exact_selected_question_component_or_support_overlap']+=1;continue
        if s.digest(row)!=item['canonical_row_sha256'] or hashlib.sha256(raw).hexdigest()!=item['raw_line_sha256']:
            raise ValueError('source row identity mismatch')
        opaque='q'+hashlib.sha256((s.NAMESPACE+'|opaque|'+s.digest(row)).encode()).hexdigest()[:20]
        public={'question':row['question'],'paragraphs':[{k:p[k] for k in ('idx','title','paragraph_text')} for p in row['paragraphs']]}
        payload=json.dumps(public,ensure_ascii=False,separators=(',',':')).encode()
        path=s.INPUTS/'public'/f'{opaque}.json';path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(payload)
        path.chmod(0o444)
        selected.append({**item,'opaque_id':opaque,'public_path':str(path),'public_file_sha256':s.sha(path),
                         'rank_sha256':hashlib.sha256((s.NAMESPACE+'|'+s.digest(row)).encode()).hexdigest(),
                         'paragraph_count':len(public['paragraphs'])})
        gold[opaque]={'source_row':row,'raw_line_utf8':raw.decode(),'answer':row['answer'],
                      'answer_aliases':row['answer_aliases'],'support_idxs':[p['idx'] for p in row['paragraphs'] if p['is_supporting']]}
        counts[hop]+=1;seen_questions.add(question);seen_steps.update(item['singlehop_ids']);seen_supports.update(item['support_paragraph_sha256'])
        if len(selected)==12:break
    if len(selected)!=12 or dict(counts)!={2:4,3:4,4:4}:raise ValueError('frozen shape unavailable')
    old=s.short().v7_study().old_module();schedule=[];tasks={arm:[] for arm in s.ARMS}
    for i,item in enumerate(selected):
        public=s.read(item['public_path'])
        order=s.ARMS[i%4:]+s.ARMS[:i%4]
        for arm in order:
            coordinate={'record_id':item['opaque_id'],'arm':arm,'hop_count':item['hop_count'],
                        'question_index':i,'seed':202609132000+i,'temperature':.5,'dispatch_order':len(schedule)}
            coordinate['id']=s.digest(coordinate);schedule.append(coordinate)
            tasks[arm].append(old.MRCRData(idx=i,name=coordinate['id'],
                prompt=s.root_prompt(public['question'],item['public_json_bytes'],arm),
                row_id=item['opaque_id'],document_sha256=item['public_file_sha256'],arm=arm).model_dump(mode='json',exclude_none=True))
    for arm,values in tasks.items():s.write_x(s.INPUTS/f'tasks_{arm}.json',values)
    s.write_x(s.INPUTS/'SCHEDULE.json',schedule)
    s.write_x(s.INPUTS/'host/HOST_GOLD.json',gold);(s.INPUTS/'host/HOST_GOLD.json').chmod(0o600)
    s.write_x(s.INPUTS/'MANIFEST.json',{'namespace':s.NAMESPACE,'source_split':'MuSiQue-Ans v1.0 dev',
        'feasibility_ready_sha256':expected,'archive_sha256':s.sha(s.ARCHIVE),'selected':selected,
        'selection_rule':'full-row hash rank, four per hop, <=5500 public Qwen tokens, no exact normalized question/singlehop-ID/support-paragraph reuse within selected12',
        'skips':dict(skipped),'answers_used_for_selection':False,'model_queries':0,
        'limitations':['structural disjointness is not semantic independence','base pretraining exposure unknown',
                      '12 selected dev questions are exploratory and research-exposed after this run',
                      'external JSON length is not actual neural input length; enforce <=8192 at every native request'],
        'license':'CC-BY-4.0 per pinned official repository; underlying source attribution retained',
        'original_public_paragraphs_preserved':True,'gold_mounted_to_runtime':False})
    print(json.dumps({'selected':len(selected),'hop_counts':dict(counts),'episodes':len(schedule)}))


if __name__=='__main__':main()
