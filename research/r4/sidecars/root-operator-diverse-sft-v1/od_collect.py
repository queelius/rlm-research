"""Counted adaptations of the qualified genuine native capture; no old source edits."""
import asyncio
import functools
import sys
import types
import od_study as s
import od_protocol as p
EDIT_COUNTS={}

@functools.lru_cache(maxsize=1)
def implementation():
    path=s.JOINT/'collect.py'
    if s.sha(path)!='f2e0d2adcfe01ee562488a98e24037781ab81f2f7daab9462eecf7098f4d93ac':raise ValueError('qualified collector source')
    source=path.read_text()
    edits={
        'imports':('import joint_protocol as p\nimport joint_study as s','import od_protocol as p\nimport od_study as s'),
        'binding':('import joint_binding as b','import od_binding as b'),
        'query_target':("p.correction(pieces,row,s.LABELS[context['target']])","p.correction(pieces,row,row['target'])"),
        'producer_spans':("kind='first_producer' if number==1 else 'producer_history';spans={}","kind='first_producer' if number==1 else 'producer_history';spans,span_ids=p.target_spans(tokenizer,reply,code)"),
        'span_identity':("if kind=='corrective' and ids!=span_ids:","if kind in ('first_producer','producer_history','corrective') and ids!=span_ids:"),
        'attempt_accounting':("response=await client.post", "record['physical_request_attempt']=True\n                        response=await client.post"),
        'query_score':("answer=sum(gold[r['id']]==context['target'] for r in context['records'] if r['user'] in row['users'])","answer=s.answer(context['records'],gold,row)"),
        'full_corpus_boundary':("args.stop==16:","args.stop==72:"),
        'full_corpus_admission':("s.corpus(16);", "s.corpus(72);"),
        'full_corpus_receipt':("examples=16,", "examples=72,"),
        'modes':("choices=('capture','free','controlled')", "choices=('capture','free')"),
        'plans':("choices=('TRAIN_PLAN.json','FREE_PLAN.json','CONTROLLED_PLAN.json','DIAGNOSTIC_PLAN.json')", "choices=('TRAIN_PLAN.json','FREE_PLAN.json')"),
    }
    for name,(old,new) in edits.items():
        expected=2 if name=='attempt_accounting' else 1
        if source.count(old)!=expected:raise ValueError('counted collector edit '+name)
        source=source.replace(old,new);EDIT_COUNTS[name]=1
    module=types.ModuleType('od_qualified_capture_composition');module.__file__=str(path)
    sys.modules[module.__name__]=module
    with s.aliases({'od_study':s,'od_protocol':p}):exec(compile(source,str(path)+'::operator-diverse', 'exec'),module.__dict__)
    return module

if __name__=='__main__':
    module=implementation();asyncio.run(module.run(module.parse_args()))
