"""Approved nine-slot table and independent scoped integer oracles."""
LABELS=['abbreviation','description and abstract concept','entity','human being','location','numeric value']
SCOPES={'ALL':['u0','u1','u2','u3'],'EVEN':['u0','u2'],'ODD':['u1','u3'],'ADJ':['u0','u1']}
def specs(split,index):
    if split not in ('train','dev','protected'):raise ValueError('declared split')
    held=split=='protected';r=index%6
    items=[('T1','threshold_users',r,None,'ALL',4 if held else 2),('T2','threshold_users',r,None,'ALL',8 if held else 6),
        ('M1','maximum_weight',r+1,None,'ALL' if held else 'EVEN',None),('M2','maximum_weight',r+1,None,'EVEN' if held else 'ODD',None),
        ('J1','conditional_weight',r+3 if held else r+2,r+2 if held else r+3,'ALL' if held else 'EVEN',None),
        ('J2','conditional_weight',r+3 if held else r+2,r+2 if held else r+3,'EVEN' if held else 'ODD',None),
        ('P1','count',r+4,None,'ADJ',None),('P2','distinct_users',r+5,None,'ODD',None),('P3','weight_sum',r,None,'ALL',None)]
    return [dict(slot=slot,operator=op,target=LABELS[a%6],target_b=LABELS[b%6] if b is not None else None,scope=scope,users=list(SCOPES[scope]),threshold=t) for slot,op,a,b,scope,t in items]
def question(row):
    scope='across all records, regardless of which of u0, u1, u2, or u3 owns the record' if row['scope']=='ALL' else 'consider only records owned by '+', '.join(row['users'])
    a=repr(row['target']);b=repr(row['target_b']);op=row['operator']
    text={'count':f'Count records whose category is {a}.','distinct_users':f'Count distinct users having at least one record whose category is {a}.',
        'weight_sum':f'Sum the weights of records whose category is {a}.',
        'threshold_users':f'How many of the scoped users have a total weight of category {a} records strictly greater than {row["threshold"]}?',
        'maximum_weight':f'What is the maximum, across the scoped users, of a user\'s total weight of category {a} records? A scoped user with no such records has total zero.',
        'conditional_weight':f'What is the total weight of category {b} records owned by scoped users who also have at least one category {a} record? Count each category {b} record once.'}[op]
    return scope[0].upper()+scope[1:]+'. '+text+' Return only Answer: N, replacing N with the exact nonnegative integer.'
def answer(records,labels,row):
    users=row['users'];a=[r for r in records if r['user'] in users and labels[r['id']]==row['target']];op=row['operator']
    if op=='count':return len(a)
    if op=='distinct_users':return len({r['user'] for r in a})
    if op=='weight_sum':return sum(r['weight'] for r in a)
    totals={u:sum(r['weight'] for r in a if r['user']==u) for u in users}
    if op=='threshold_users':return sum(v>row['threshold'] for v in totals.values())
    if op=='maximum_weight':return max(totals.values(),default=0)
    if op=='conditional_weight':return sum(r['weight'] for r in records if r['user'] in {x['user'] for x in a} and labels[r['id']]==row['target_b'])
    raise ValueError('declared operator')
def enumerated_answer(records,labels,row):
    counts={u:0 for u in row['users']};weights=dict.fromkeys(counts,0);bweights=dict.fromkeys(counts,0)
    for r in records:
        u=r['user']
        if u not in counts:continue
        if labels[r['id']]==row['target']:counts[u]+=1;weights[u]+=r['weight']
        if labels[r['id']]==row['target_b']:bweights[u]+=r['weight']
    return {'count':lambda:sum(counts.values()),'distinct_users':lambda:sum(v!=0 for v in counts.values()),'weight_sum':lambda:sum(weights.values()),
        'threshold_users':lambda:sum(v>=row['threshold']+1 for v in weights.values()),'maximum_weight':lambda:max([0,*weights.values()]),
        'conditional_weight':lambda:sum(bweights[u] for u in counts if counts[u]>0)}[row['operator']]()
