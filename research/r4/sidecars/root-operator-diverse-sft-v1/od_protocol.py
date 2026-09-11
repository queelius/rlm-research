"""Label-blind fixed corpus and trusted authored live-state actions."""
import hashlib
import json
import functools
import io
import tokenize

NAMESPACE='operator-diverse-sft-20260910-v1'
LAYOUTS=(
    dict(records='records',labels='observed_labels',selected='qualifying',result='answer',batch='batch',piece='piece',child='child'),
    dict(records='rows',labels='category_state',selected='selected_rows',result='total',batch='chunk',piece='chunk_labels',child='reply'),
    dict(records='items',labels='live_map',selected='matches',result='scalar',batch='section',piece='decoded',child='response'),
    dict(records='public_rows',labels='accumulator',selected='eligible',result='result',batch='part',piece='part_map',child='child_result'))

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def question(q,template):
    scope=('all records, regardless of which user owns them' if q['scope']=='all' else
           'records belonging to user '+repr(q['users'][0]) if q['scope']=='single' else
           'records belonging to the union of users '+ ' and '.join(map(repr,q['users']))+' (each record once)')
    operation={'count':'Count qualifying records','distinct':'Count distinct users having at least one qualifying record','weight':'Sum the visible record weight values of qualifying records'}[q['operator']]
    target=repr(q['target'])
    variants=(f'Consider {scope}. A record qualifies when its question category is {target}. {operation}.',
              f'Use {scope}. Keep only records whose question category is {target}. {operation}.',
              f'The scope is {scope}. Within this scope, the qualifying category is {target}. {operation}.',
              f'For {scope}, treat a record as qualifying if its question category is {target}. {operation}.')
    return variants[template]+' If none qualify, the result is zero. Return only Answer: N, replacing N with the exact nonnegative integer.'

def build(source):
    public=source['PUBLIC.json'];by_id={c['id']:c for c in public};training=[];free=[];queries={}
    candidates={r['task_name']:r for window in source['PLANS.json']['training'].values() for r in window}
    for ci in range(12):
        context=by_id[f'training-{ci:02}'];names=sorted(k for k in candidates if candidates[k]['context_id']==context['id'])
        if len(names)!=3 or context['size']!=16:raise ValueError('fixed three supported tasks and16 records')
        for task in names:
            q=source['QUERIES.json'][task]
            for wi,width in enumerate((4,16)):
                template=(ci+wi)%4;layout=(ci+ci//4+wi)%4
                row=dict(context_id=context['id'],task_name=task,family=task.split(':')[1],operator=q['operator'],scope=q['scope'],users=q['users'],target=q['target'],width=width,
                    names=LAYOUTS[layout],template=template,layout=layout,question=question(q,template),metadata_error=False,role='native',evidence='raw',
                    seed=981451101+len(training),split='training',namespace=NAMESPACE)
                row['id']=digest(row);queries[row['id']]=q;training.append(row)
    for ci in range(4,12):
        context=by_id[f'readout-{ci:02}'];candidates_free={r['task_name']:r for r in source['PLANS.json']['readout'] if r['context_id']==context['id'] and r['heldout_cell']}
        if len(candidates_free)!=3:raise ValueError('three held-out operator/scope cells')
        for task in sorted(candidates_free):
            q=source['QUERIES.json'][task];template=(ci-4)%4
            row={**candidates_free[task],**q,'template':template,'question':question(q,template),'seed':981451501+len(free),'repeat':0,'namespace':NAMESPACE,'role':'native','evidence':'raw'}
            row.pop('id');row['id']=digest(row);queries[row['id']]=q;free.append(row)
    gate=[r for operator,ci in [('count',0),('distinct',0),('weight',1)] for r in training if r['operator']==operator and r['context_id']==f'training-{ci:02}']
    groups={g['id']:set(g['group_ids']) for g in source['GROUPS.json']}
    train_groups=set.union(*(groups[f'training-{i:02}'] for i in range(12)));read_groups=set.union(*(groups[f'readout-{i:02}'] for i in range(4,12)))
    if len(train_groups)!=192 or train_groups & read_groups:raise ValueError('source split overlap/cardinality')
    selected={r['context_id'] for r in training+free}
    return {'TRAIN_PLAN.json':training,'FREE_PLAN.json':free,'GATE_PLAN.json':gate,'QUERIES.json':queries,
        'PUBLIC.json':[c for c in public if c['id'] in selected],'GROUPS.json':[g for g in source['GROUPS.json'] if g['id'] in selected]}

def producer(row,index):
    n=row['names'];start=index*row['width'];end=start+row['width']
    initial=('import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\n'+n['records']+' = json.load(open("records.json"))\n'+n['labels']+' = {}\n') if index==0 else ''
    return initial+f'{n["batch"]} = {n["records"]}[{start}:{end}]\n{n["child"]} = await rlm(request_for({n["batch"]}))\n{n["piece"]} = strict_map({n["child"]}.answer, [record["id"] for record in {n["batch"]}])\n{n["labels"]}.update({n["piece"]})\nprint(json.dumps({n["labels"]}, sort_keys=True))'

def reduction(row):
    n=row['names'];selected=n['selected'];result=n['result']
    code=f'{selected} = [record for record in {n["records"]} if record["user"] in {row["users"]!r} and {n["labels"]}[record["id"]] == {row["target"]!r}]\n'
    value={'count':f'len({selected})','distinct':f'len({{record["user"] for record in {selected}}})','weight':f'sum(record["weight"] for record in {selected})'}[row['operator']]
    return code+f'{result} = {value}\nprint({result})'

@functools.lru_cache(maxsize=1)
def shared():
    import od_study as s
    return s.load('od_qualified_joint_protocol',s.JOINT/'joint_protocol.py','9cd776cf132784d0c589266d89e2e9613fd83a6f3126ff1a5f95657d6359a8b7',{'joint_study':s.joint()})
def row(*args,**kwargs):return shared().row(*args,**kwargs)
def scalar(text):return shared().scalar(text)
def layout(coordinate):return shared().layout(coordinate)
def visible_maps(observations,context):return shared().visible_maps(observations,context)
def correction(pieces,coordinate,target):
    if coordinate['target']!=target:raise ValueError('target drift')
    return reduction(coordinate),{'payload_lines':[]}
def physical_cost(records):
    # Legacy field name is not a provider billing claim; count failed dispatched requests too.
    return shared().physical_cost([{**r,'paid_model_call':r.get('physical_request_attempt',r.get('paid_model_call',False))} for r in records])

def target_spans(tokenizer,wire,code):
    encoded=tokenizer(wire,add_special_tokens=False,return_offsets_mapping=True)
    escaped=json.dumps(code)[1:-1];begin=wire.index(escaped);end=begin+len(escaped);starts=[];position=begin;lines=code.splitlines()
    for line in lines:starts.append(position);position+=len(json.dumps(line)[1:-1])+2
    literals=[]
    for token in tokenize.generate_tokens(io.StringIO(code).readline):
        if token.type in (tokenize.STRING,tokenize.NUMBER):
            (line,a),(last,b)=token.start,token.end
            if line!=last:raise ValueError('single-line literals required')
            literals.append((starts[line-1]+len(json.dumps(lines[line-1][:a])[1:-1]),starts[line-1]+len(json.dumps(lines[line-1][:b])[1:-1])))
    spans={'mechanism':[],'copied_literals':[],'other':[],'payload':[]}
    for i,(a,b) in enumerate(encoded['offset_mapping']):
        kind='mechanism' if begin<=a<b<=end else 'other'
        if kind=='mechanism' and any(a<y and b>x for x,y in literals):kind='copied_literals' if any(x<=a<b<=y for x,y in literals) else 'other'
        spans[kind].append(i)
    spans['other'].append(len(encoded['input_ids']))
    return spans,encoded['input_ids']+[151645]
