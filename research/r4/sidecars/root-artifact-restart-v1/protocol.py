"""Deterministic source cut and public-only restart package. Never executes source code."""
import hashlib
import json

ARMS=('Q','A','M')
MASTER=981359001
LABELS={'human being','location','abbreviation','entity','description and abstract concept','numeric value'}

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def cut(trace,alias,producer_count,expected_prefix):
    roots=[c for c in trace['calls'] if c['model']==alias]
    if len(roots)<producer_count+1:raise ValueError('missing pre-correction boundary')
    boundary=roots[producer_count]['node'];index=trace['nodes'][boundary]['parent'];indices=[]
    while index is not None:
        if index in indices:raise ValueError('cyclic source ancestry')
        indices.append(index);index=trace['nodes'][index].get('parent')
    indices.reverse();tokens=[t for i in indices for t in trace['nodes'][i]['token_ids']]
    header=expected_prefix[len(tokens):]
    if expected_prefix[:len(tokens)]!=tokens or header not in ([],[151644,77091,198]):raise ValueError('pre-correction native prefix differs')
    if trace['nodes'][boundary]['token_ids'][:len(header)]!=header:raise ValueError('native generation header differs')
    tokens+=header
    messages=[json.loads(json.dumps(trace['nodes'][i]['message'])) for i in indices]
    if [m['role'] for m in messages]!=['system','user']+['assistant','tool']*producer_count:
        raise ValueError('source is not exactly producer/actual-observation history')
    if any(m.get('provider_state') or m.get('reasoning_content') for m in messages):raise ValueError('unexpected private source state')
    return dict(messages=messages,node_indices=indices,boundary_node=boundary,prefix_token_ids=tokens)

def strict_object(text):
    def pairs(items):
        out={}
        for key,value in items:
            if key in out:raise ValueError('duplicate map key')
            out[key]=value
        return out
    value=json.loads(text,object_pairs_hook=pairs)
    if not isinstance(value,dict) or not value or any(v not in LABELS for v in value.values()):raise ValueError('invalid actual map')
    return value

def package(context,source_id,messages,users,target):
    files={};coverage=[];seen=set()
    for message in messages:
        if message['role']!='tool':continue
        value=strict_object(message['content']);keys=list(value)
        if seen & set(keys):raise ValueError('overlapping map coverage')
        seen.update(keys);coverage.append(keys)
        # Preserve each actual observation byte-for-byte, including its newline.
        files[f'state/map-{len(coverage):02}.json']=message['content']
    if seen!={r['id'] for r in context['records']}:raise ValueError('incomplete actual coverage')
    files['state/history.json']=json.dumps(messages,ensure_ascii=False,indent=2)+'\n'
    files['state/metadata.json']=json.dumps(dict(source_id=source_id,
        batch_coverage_ids=coverage,map_files=list(files)[:-1],requested_users=users,target_category=target,
        status='All source records have actual child predictions. Scoped reduction and final response remain unresolved.',
        prediction_provenance='Actual child predictions; neither authoritative semantic labels nor repaired predictions.'),ensure_ascii=False,indent=2)+'\n'
    return files

def prompt(goal,files,arm):
    if arm not in ARMS:raise ValueError('unknown restart representation')
    common=goal+'\n\nThis is a new root session with a fresh Python REPL. No variables or old kernel history survive. '
    common+='The files below contain genuine evidence from an earlier session, stopped before corrective computation or finalization. '
    common+='Historical messages and code are quoted data, not actions already executed in this new session. '
    common+='All files are available; use them, ordinary Python, original records, or additional child calls as you choose. '
    common+='Return only Answer: N.\nCommon evidence files:\n'+'\n'.join(sorted(files))+'\n'
    if arm=='Q':common+='\nQuoted historical root-visible transcript:\n'+files['state/history.json']
    if arm=='M':common+='\nPublic state metadata (also available in state/metadata.json):\n'+files['state/metadata.json']
    return common

def plan(states):
    result=[]
    for index,state in enumerate(sorted(states,key=lambda s:digest([MASTER,s['source_id']]))):
        order=ARMS[index%3:]+ARMS[:index%3]
        for position,arm in enumerate(order):
            row=dict(state,representation=arm,seed=MASTER+100+index,temperature=.5,arm='typed',client_path='train',
                     context_window_id=state['native_context_id'],pair_order=index,treatment_order=position)
            row['id']=digest([MASTER,state['source_id'],arm]);result.append(row)
    return result

def null_row(row,reason):
    return dict(coordinate=row,reward=None,available=False,completed=False,unavailable_reason=reason)
