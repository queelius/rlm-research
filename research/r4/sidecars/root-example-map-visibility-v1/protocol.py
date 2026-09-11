"""Eight blocks, balanced2x2 prompt ablation; no gold enters prompt construction."""
import hashlib
import json
import re

MASTER=981342001


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def plan_for(contexts):
    blocks=[(ci,c,family) for ci,c in enumerate(contexts) for family in ('single_user','union')]
    ranked=sorted(range(8),key=lambda i:digest([MASTER,'block',blocks[i][1]['id'],blocks[i][2]]))
    rank={block:i for i,block in enumerate(ranked)}
    cells=sorted([(False,False),(False,True),(True,False),(True,True)],key=lambda v:digest([MASTER,'cells',v]))
    rows=[]
    for bi,(ci,context,family) in enumerate(blocks):
        shift=rank[bi]%4;ordered=cells[shift:]+cells[:shift]
        for order,(example,inline) in enumerate(ordered):
            row=dict(context_id=context['id'],context_window_id=98133000+ci,stratum=context['stratum'],helper_partition=context['helper_partition'],family=family,pair_id=digest([MASTER,context['id'],family]),example=example,inline=inline,arm='typed',treatment_order=order,seed=981342201+bi,temperature=.5,client_path='train')
            row['id']=digest(row);rows.append(row)
    return rows


def prompt(base,row,map_bytes):
    if not isinstance(map_bytes,bytes):raise ValueError('frozen map bytes required')
    text=base.replace('id, synthetic user metadata, and original question text','id, user, and text fields').replace('No source semantic labels are present.','records.json and context.txt contain no category labels.')
    if not row['example']:
        text,n=re.subn(r'\n\nOptional API example \(first four records only, NOT the final answer\):\n```python\n.*?\n```\n\n','\n\n',text,flags=re.S)
        if n!=1:raise ValueError('one exact optional example block required')
    text+='\n\nlabels.json contains child predictions from one previously completed native c32 classification, not authoritative dataset labels. It is a JSON object mapping every public record ID to its category. Select the requested records using the user field in records.json. You may use labels.json, ordinary Python, or additional child calls. Submit your own final Answer: N.'
    if row['inline']:
        text+='\nThe following is the identical JSON content of labels.json:\n<supplied_labels_json>\n'+map_bytes.decode('utf-8')+'\n</supplied_labels_json>'
    return text
