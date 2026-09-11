"""Authored cumulative state in the actual REPL; reduction never embeds a map literal."""
import ast
import io
import json
import tokenize
import joint_study as s
old=s.load('joint_immutable_native_contract',s.BASE_CORRECTIVE/'protocol.py','21f1789587e60ac49e3443c375db7c08afef622a75d7457531f6c9b3d6ddc6a1')
row,scalar,physical_cost,verify_replay,layout=old.row,old.scalar,old.physical_cost,old.verify_replay,old.layout

def producer(row,index):
    variable=row['variable'];start=index*row['width'];end=start+row['width']
    initial=('import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\n'
             'records = json.load(open("records.json"))\n'+variable+' = {}\n') if index==0 else ''
    return initial+f'batch = records[{start}:{end}]\nchild = await rlm(request_for(batch))\nbatch_map = strict_map(child.answer, [record["id"] for record in batch])\n{variable}.update(batch_map)\nprint(json.dumps({variable}, sort_keys=True))'

def visible_maps(observations,context):
    expected={r['id'] for r in context['records']};previous={};pieces=[]
    for text in observations:
        lines=[line for line in text.splitlines() if line.startswith('{')]
        if len(lines)!=1:raise ValueError('one genuine cumulative map observation required')
        value=json.loads(lines[0])
        if not isinstance(value,dict) or not set(previous)<set(value) or not set(value)<=expected or any(value.get(k)!=v for k,v in previous.items()):raise ValueError('cumulative acquisition lost/changed prior observation')
        if any(v not in s.LABELS.values() for v in value.values()):raise ValueError('noncanonical observed category')
        pieces.append(value);previous=value
    if set(previous)!=expected:raise ValueError('actual full cumulative state required')
    return pieces,previous

def correction(pieces,row,target):
    code=('requested_ids = [record["id"] for record in records if record["user"] in '+repr(row['users'])+']\n'
          'count = sum('+row['variable']+'[record_id] == '+repr(target)+' for record_id in requested_ids)\nprint(count)')
    ast.parse(code);return code,dict(mechanism_lines=[0,1,2],payload_lines=[])

def target_spans(tokenizer,wire,code):
    encoded=tokenizer(wire,add_special_tokens=False,return_offsets_mapping=True)
    escaped=json.dumps(code)[1:-1];begin=wire.index(escaped);end=begin+len(escaped)
    starts=[];position=begin;lines=code.splitlines()
    for line in lines:starts.append(position);position+=len(json.dumps(line)[1:-1])+2
    literals=[]
    for token in tokenize.generate_tokens(io.StringIO(code).readline):
        if token.type==tokenize.STRING:
            (line,a),(last,b)=token.start,token.end
            if line!=last:raise ValueError('single-line string literals only')
            literals.append((starts[line-1]+len(json.dumps(lines[line-1][:a])[1:-1]),starts[line-1]+len(json.dumps(lines[line-1][:b])[1:-1])))
    spans={'mechanism':[],'copied_literals':[],'other':[],'payload':[]}
    for i,(a,b) in enumerate(encoded['offset_mapping']):
        kind='mechanism' if begin<=a<b<=end else 'other'
        if kind=='mechanism' and any(a<y and b>x for x,y in literals):kind='copied_literals' if any(x<=a<b<=y for x,y in literals) else 'other'
        spans[kind].append(i)
    spans['other'].append(len(encoded['input_ids']))
    return spans,encoded['input_ids']+[151645]

def null_row(row,reason):return dict(coordinate=row,available=False,reward=None,reason=reason)
