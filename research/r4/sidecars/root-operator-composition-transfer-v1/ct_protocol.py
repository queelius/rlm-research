"""Six prospective operators; deterministic host-only scoring, never prompt algorithms."""
OPERATORS=('count','distinct_users','weight_sum','threshold_users','maximum_weight','conditional_weight')
TARGETS=('human being','entity','location','numeric value')
USERS=('u0','u1','u2','u3')

def specs(index):
    a,b=TARGETS[index%4],TARGETS[(index+1)%4]
    common='Across all records, regardless of which user owns the record, '
    questions=[
        f'how many records have category {a}?',
        f'how many distinct users have at least one record with category {a}?',
        f'what is the sum of the weights of records with category {a}?',
        f'how many of u0, u1, u2, and u3 have a total weight of their {a} records strictly greater than 5? A user with no such records has total 0.',
        f'what is the largest total weight of {a} records belonging to any one of u0, u1, u2, and u3? A user with no such records has total 0. Return the largest total, not a user ID.',
        f'what is the sum of the weights of {b} records belonging to users who also have at least one {a} record? Count each qualifying {b} record once. Return 0 if there are none.',
    ]
    return [dict(operator=op,target=a,target_b=b,scope='all',users=list(USERS),panel='primitive' if i<3 else 'composition',question=common+q) for i,(op,q) in enumerate(zip(OPERATORS,questions))]

def answer(records,labels,row):
    op=row['operator'];a=row['target'];chosen=[r for r in records if labels[r['id']]==a]
    if op=='count':return len(chosen)
    if op=='distinct_users':return len({r['user'] for r in chosen})
    if op=='weight_sum':return sum(r['weight'] for r in chosen)
    totals={u:sum(r['weight'] for r in chosen if r['user']==u) for u in USERS}
    if op=='threshold_users':return sum(v>5 for v in totals.values())
    if op=='maximum_weight':return max(totals.values())
    if op=='conditional_weight':
        users={r['user'] for r in chosen}
        return sum(r['weight'] for r in records if r['user'] in users and labels[r['id']]==row['target_b'])
    raise ValueError('unplanned operator')

def enumerated_answer(records,labels,row):
    """Independent per-user iterative oracle, not called by the model or live scorer."""
    counts=[0]*4;weights=[0]*4;bweights=[0]*4
    for record in records:
        j=USERS.index(record['user']);label=labels[record['id']]
        if label==row['target']:
            counts[j]+=1;weights[j]+=record['weight']
        if label==row.get('target_b'):bweights[j]+=record['weight']
    op=row['operator']
    if op=='count':return sum(counts)
    if op=='distinct_users':return sum(1 for n in counts if n!=0)
    if op=='weight_sum':return sum(weights)
    if op=='threshold_users':return len([u for u in range(4) if weights[u]>=6])
    if op=='maximum_weight':return sorted(weights)[-1]
    if op=='conditional_weight':return sum(bweights[u] for u in range(4) if counts[u]>0)
    raise ValueError('unplanned operator')

def physical_cost(records):
    import ct_study as s
    return s.dr.protocol().physical_cost(records)
