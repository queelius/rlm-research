"""Fixed public tasks; strict endpoint accuracy is not trace-flag availability."""
import re
import rv_study as s
FAMILIES=('count-union','distinct-all','weight-single')
def host():return s.read(s.QSR/'HOST_GOLD.json')
def plan():
    out=[]
    for policy in ('base','rlm'):
        for i in range(24):
            row=dict(policy=policy,context_id=f'readout-{4+i//3:02d}',family=FAMILIES[i%3],seed=2026091101+i,index=i)
            row['id']=s.digest(row);out.append(row)
    return out
def gold(row):return host()[row['context_id']]['answers'][row['family']]
def answer(records,labels,q):
    selected=[r for r in records if r['user'] in q['users'] and labels[r['id']]==q['target']]
    if q['operator']=='count':return len(selected)
    if q['operator']=='distinct':return len({r['user'] for r in selected})
    if q['operator']=='weight':return sum(r['weight'] for r in selected)
    raise ValueError('operator')
def task(row):
    c=next(c for c in s.read(s.QSR/'PUBLIC.json') if c['id']==row['context_id']);q=s.read(s.QSR/'QUERIES.json')[row['context_id']+':'+row['family']]
    scope='any of users u0, u1, u2, and u3 (all records)' if q['scope']=='all' else ('user '+repr(q['users'][0]) if q['scope']=='single' else 'the union of users '+repr(q['users'][0])+' and '+repr(q['users'][1])+' (each record once)')
    op={'count':'Count qualifying records','distinct':'Count distinct users having at least one qualifying record','weight':'Sum the visible record weight values of qualifying records'}[q['operator']]
    query="The context is JSONL, one record per line, with fields id, user, text, weight. text is a question; its category concerns the kind of answer it requests, not the topic or words alone. Categories are 'numeric value', 'entity', 'location', 'description and abstract concept', 'abbreviation', and 'human being'. Records contain no category labels.\n"
    query+=f"Among records belonging to {scope}, a record qualifies when its question category is {q['target']!r}. {op}. If none qualify, the result is zero. The final answer content must be only Answer: N, replacing N with the exact nonnegative integer."
    return dict(context=c['text'],query=query)
def score(final,available,expected):
    if not available:return dict(available=False,format_ok=None,value=None,correct=None)
    match=re.fullmatch(r'Answer: (0|[1-9][0-9]*)',final.strip()) if isinstance(final,str) else None
    value=int(match[1]) if match else None
    return dict(available=True,format_ok=bool(match),value=value,correct=bool(match) and value==expected)
def null(row,reason):return dict(coordinate=row,score=score(None,False,gold(row)),reason=reason)
