"""Exact old/new endpoints: field schema × map-contract wording, three paired seeds."""
import hashlib
import json

MASTER=981347001


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def plan_for(contexts):
    blocks=[(ci,c,family,rep) for ci,c in enumerate(contexts) for family in ('single_user','union') for rep in range(3)]
    ranked=sorted(range(24),key=lambda i:digest([MASTER,'launch',blocks[i][1]['id'],blocks[i][2],blocks[i][3]]))
    cells=sorted([(False,False),(False,True),(True,False),(True,True)],key=lambda v:digest([MASTER,'cells',v]))
    rows=[]
    for position,bi in enumerate(ranked):
        ci,context,family,rep=blocks[bi]
        shift=position%4
        for order,(schema,map_contract) in enumerate(cells[shift:]+cells[:shift]):
            block_id=digest([MASTER,context['id'],family])
            row=dict(context_id=context['id'],context_window_id=98133000+ci,stratum=context['stratum'],
                     helper_partition=context['helper_partition'],family=family,block_id=block_id,
                     pair_id=digest([block_id,rep]),repeat=rep,schema=schema,map_contract=map_contract,
                     arm='typed',treatment_order=order,pair_launch_order=position,seed=981347201+bi,
                     temperature=.5,client_path='train')
            row['id']=digest(row)
            rows.append(row)
    return rows


def prompt(old,row):
    changes=[]
    if row['schema']:
        changes += [('id, synthetic user metadata, and original question text','id, user, and text fields'),
                    ('using their public user metadata in records.json','using the user field in records.json')]
    if row['map_contract']:
        changes += [('No source semantic labels are present.','records.json and context.txt contain no category labels.'),
                    ('Supplied-map diagnostic treatment: labels.json is a JSON object mapping every public record ID to its category. Source: one actual frozen native c32 child acquisition; labels may disagree with dataset.',
                     'labels.json contains child predictions from one previously completed native c32 classification, not authoritative dataset labels. It is a JSON object mapping every public record ID to its category.'),
                    ('You may use the supplied map and ordinary Python.','You may use labels.json, ordinary Python, or additional child calls.')]
    text=old
    for before,after in changes:
        if text.count(before)!=1:raise ValueError('expected exactly one frozen phrase: '+before)
        text=text.replace(before,after)
    return text
