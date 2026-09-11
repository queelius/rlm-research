"""Explicit authored-state/target contract; never reads host semantic gold."""
import ast
import json
import re
import io
import tokenize

def requested(context,row):
    return [r['id'] for r in context['records'] if r['user'] in row['users']]

def producer(row,index):
    width=row['width'];start=index*width;variable=row['variable']
    code=('import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\n'
          'records = json.load(open("records.json"))\n'
          f'batch = records[{start}:{start+width}]\nchild = await rlm(request_for(batch))\n'
          f'{variable} = strict_map(child.answer, [record["id"] for record in batch])\n'
          f'print(json.dumps({variable}, sort_keys=True))')
    return code

def layout(row):
    count=16//row['width'];error=int(row['metadata_error'])
    return dict(child_calls=count,error_turns=error,root_turns=count+error+2,corrective_turn=count+error+1,terminal_turn=count+error+2)

def error_probe():return 'records[0]["synthetic user metadata"]'

def verify_replay(actual,source):
    if actual!=source:raise ValueError('shared child entire native request differs: model, tokens, sampling/caps/cache; no metadata exceptions')

def physical_cost(records):
    paid=[r for r in records if r['paid_model_call']]
    return dict(calls=len(paid),input_tokens=sum(len(r['body']['token_ids']) for r in paid),
        output_tokens_known=sum(len(c['token_ids']) for r in paid for c in r.get('response',{}).get('choices',[])),
        output_unknown_calls=sum(not r.get('response',{}).get('choices') for r in paid),cached_tokens=None,
        token_basis='exact physical input and returned completion token IDs; cache hit usage unknown, no invented zero')

def visible_maps(observations,context):
    expected={r['id'] for r in context['records']};merged={};pieces=[]
    for text in observations:
        # Each genuine producer prints one compact JSON line before any authored error.
        lines=[line for line in text.splitlines() if line.startswith('{')]
        if len(lines)!=1:raise ValueError('one actually visible map line required')
        def pairs(items):
            value={}
            for k,v in items:
                if k in value:raise ValueError('duplicate child key')
                value[k]=v
            return value
        value=json.loads(lines[0],object_pairs_hook=pairs)
        if not isinstance(value,dict) or set(value)&set(merged):raise ValueError('map overlap/non-object')
        if any(v not in ('human being','location','abbreviation','entity','description and abstract concept','numeric value') for v in value.values()):raise ValueError('noncanonical child label')
        pieces.append(value);merged.update(value)
    if set(merged)!=expected:raise ValueError('full visible map required; no hidden data repair')
    return pieces,merged

def correction(pieces,row,target):
    # Data literals are actual observed child labels; fresh local names need no hidden state.
    payload=repr(pieces)
    lines=['import json','records = json.load(open("records.json"))','visible_maps = '+payload,
        'by_id = {}','for piece in visible_maps:','    by_id.update(piece)',
        'requested_ids = [record["id"] for record in records if record["user"] in '+repr(row['users'])+']',
        'count = sum(by_id[record_id] == '+repr(target)+' for record_id in requested_ids)','print(count)']
    code='\n'.join(lines);ast.parse(code)
    return code,dict(payload_line=2,mechanism_lines=list(range(3,9)))

def scalar(text):
    match=re.fullmatch(r'\s*([0-9]+)\s*',text)
    if not match:raise ValueError('actual corrective tool observation must be scalar')
    return int(match[1])

def row(identity,prefix,target,kind,span_indices=None):
    if not prefix or not target or target[-1]!=151645 or len(prefix)+len(target)>8192:raise ValueError('native target boundary/no truncation')
    return dict(id=identity,kind=kind,input_ids=prefix+target,labels=[-100]*len(prefix)+target,
        loss_mask=[0]*len(prefix)+[1]*len(target),prompt_length=len(prefix),target_tokens=len(target),
        span_indices=span_indices or {},provenance='authored current-action SFT; preceding sampled/authored history masked')

def target_spans(tokenizer,wire,code):
    # Fast tokenizer offsets align actual wire suffix tokens to escaped code lines.
    encoded=tokenizer(wire,add_special_tokens=False,return_offsets_mapping=True)
    escaped=json.dumps(code)[1:-1];begin=wire.index(escaped)
    spans={'mechanism':[],'payload':[],'copied_literals':[],'other':[]};ranges=[];position=begin;line_starts=[]
    for i,line in enumerate(code.splitlines()):
        escaped_line=json.dumps(line)[1:-1];end=position+len(escaped_line)
        kind='payload' if i==2 else 'mechanism' if i>=3 else 'other'
        line_starts.append(position);ranges.append((position,end,kind));position=end+2 # literal backslash-n in JSON
    literals=[];lines=code.splitlines()
    for token in tokenize.generate_tokens(io.StringIO(code).readline):
        line,start=token.start;last,end=token.end
        if token.type==tokenize.STRING and line==last and line>=4:
            a=line_starts[line-1]+len(json.dumps(lines[line-1][:start])[1:-1])
            b=line_starts[line-1]+len(json.dumps(lines[line-1][:end])[1:-1]);literals.append((a,b))
    for i,(start,end) in enumerate(encoded['offset_mapping']):
        classes={kind for a,b,kind in ranges if start<b and end>a}
        kind=next(iter(classes)) if len(classes)==1 else 'other'
        if kind=='mechanism' and any(start<b and end>a for a,b in literals):
            kind='copied_literals' if any(a<=start and end<=b for a,b in literals) else 'other'
        spans[kind].append(i)
    spans['other'].append(len(encoded['input_ids'])) # native EOS
    return spans,encoded['input_ids']+[151645]
