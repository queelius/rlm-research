"""Host-only three-operator scorer with actual per-row threshold; no prompt algorithm."""
USERS=('u0','u1','u2','u3')
def question(row):
    a,b,t=row['target'],row['target_b'],row['threshold'];op=row['operator'];common='Across all records, regardless of which user owns the record, '
    if op=='threshold_users':return common+f'how many of u0, u1, u2, and u3 have a total weight of their {a} records strictly greater than {t}? A user with no such records has total 0.'
    if op=='maximum_weight':return common+f'what is the largest total weight of {a} records belonging to any one of u0, u1, u2, and u3? A user with no such records has total 0. Return the largest total, not a user ID.'
    if op=='conditional_weight':return common+f'what is the sum of the weights of {b} records belonging to users who also have at least one {a} record? Count each qualifying {b} record once. Return 0 if there are none.'
    raise ValueError('unplanned composed operator')
def answer(records,labels,row):
    if row['users']!=list(USERS):raise ValueError('all four actual users required')
    chosen=[r for r in records if labels[r['id']]==row['target']];totals={u:sum(r['weight'] for r in chosen if r['user']==u) for u in USERS}
    if row['operator']=='threshold_users':return sum(v>row['threshold'] for v in totals.values())
    if row['operator']=='maximum_weight':return max(totals.values())
    if row['operator']=='conditional_weight':
        users={r['user'] for r in chosen};return sum(r['weight'] for r in records if r['user'] in users and labels[r['id']]==row['target_b'])
    raise ValueError('unplanned composed operator')
def enumerated_answer(records,labels,row):
    counts=[0]*4;weights=[0]*4;bweights=[0]*4
    for r in records:
        i=USERS.index(r['user']);label=labels[r['id']]
        if label==row['target']:counts[i]+=1;weights[i]+=r['weight']
        if label==row['target_b']:bweights[i]+=r['weight']
    if row['operator']=='threshold_users':return len([v for v in weights if v>=row['threshold']+1])
    if row['operator']=='maximum_weight':return sorted(weights)[-1]
    if row['operator']=='conditional_weight':return sum(w for n,w in zip(counts,bweights) if n>0)
    raise ValueError('unplanned composed operator')
