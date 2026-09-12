"""Strict format/status accounting with unchanged official MuSiQue metrics."""
from collections import Counter
import copy
import functools
import json
import sys
import musique_study as s


@functools.lru_cache(None)
def metric_classes():
    # These standard-library source files were fully inspected before import.
    # Avoid a preexisting research module named metrics changing official imports.
    names={name:module for name,module in sys.modules.items() if name=='metrics' or name.startswith('metrics.')}
    for name in names:sys.modules.pop(name)
    old_path=list(sys.path)
    try:
        sys.path.insert(0,str(s.REPO))
        from metrics.answer import AnswerMetric
        from metrics.support import SupportMetric
        return AnswerMetric,SupportMetric
    finally:
        for name in list(sys.modules):
            if name=='metrics' or name.startswith('metrics.'):sys.modules.pop(name)
        sys.modules.update(names);sys.path[:]=old_path


def strict_pairs(pairs):
    value={}
    for k,v in pairs:
        if k in value:raise ValueError('duplicate JSON key')
        value[k]=v
    return value


def score_final(text,gold,n_paragraphs):
    zero={'valid_json':False,'answer_em':0.,'answer_f1':0.,'support_em':0.,'support_f1':0.}
    try:
        value=json.loads(text,object_pairs_hook=strict_pairs)
        if set(value)!={'answer','support_idxs'} or not isinstance(value['answer'],str):raise ValueError('final schema')
        indices=value['support_idxs']
        if not isinstance(indices,list) or any(type(i)!=int or not 0<=i<n_paragraphs for i in indices):raise ValueError('support index schema')
        if len(set(indices))!=len(indices):raise ValueError('duplicate support index')
    except (ValueError,TypeError):return zero
    AnswerMetric,SupportMetric=metric_classes();am=AnswerMetric();sm=SupportMetric()
    am(value['answer'],[gold['answer']]+gold['answer_aliases']);sm(indices,gold['support_idxs'])
    em,f1=am.get_metric();spem,spf1=sm.get_metric()
    return dict(valid_json=True,parsed=value,answer_em=em,answer_f1=f1,support_em=spem,support_f1=spf1)


def node_depth(nodes,index,visiting=None):
    visiting=set() if visiting is None else set(visiting)
    if index in visiting:raise ValueError('causal depth cycle')
    visiting.add(index);node=nodes[index]
    depth=node_depth(nodes,node['parent'],visiting) if node.get('parent') is not None else 0
    for edge in node.get('semantic_parents',[]):
        if edge['type']=='subagent_call':depth=max(depth,1+node_depth(nodes,edge['node'],visiting))
    return depth


def inspect(raw,coordinate,native_rows):
    rows=[r for r in native_rows if r['coordinate_id']==coordinate['id']]
    returned=[r for r in rows if r['status']=='returned'];refused=[r for r in rows if r['status']=='refused']
    errors=[r for r in rows if r['status'] not in ('returned','refused')]
    traces=raw.get('traces') or [];trace=traces[0] if len(traces)==1 else {}
    stop=trace.get('stop_condition');root_reply=trace.get('root_reply')
    trace_errors=[*raw.get('errors',[]),*(e for t in traces for e in t.get('errors',[]))]
    if coordinate['arm']=='question_only':
        mapping={'complete':len(returned)==1 and not errors,'matches':[],'root_actions':len(returned),'child_actions':0}
        depths={'0':len(returned)}
        root_reply=raw.get('direct_response',{}).get('message',{}).get('content')
        stop='agent_completed' if raw.get('ok') else 'error'
    else:
        mapping=s.causal().map_trace(trace,returned,max_actions=6)
        depths=dict(Counter(str(node_depth(trace['nodes'],m['node'])) for m in mapping['matches']))
    physical=[r for r in rows if r.get('physical_forward_started')]
    cap=1 if coordinate['arm']=='question_only' else 6
    authenticated=bool(returned and mapping['complete'] and not errors and len(physical)<=cap)
    maximum=max(map(int,depths),default=0)
    if coordinate['arm']!='question_only' and maximum>int(coordinate['arm'][-1]):authenticated=False
    # Unknown errors/stops are unavailable; a framework cap with clean native mapping
    # is an observed finite-horizon failure. Guard-refusal error records stay explicit;
    # if they prevent clean trace mapping, availability remains unknown, not fabricated zero.
    available=False;failure='infrastructure_or_unmapped';score=None
    if authenticated and not trace_errors:
        if stop=='agent_completed' and raw.get('ok'):
            available=True;failure=None
        elif stop in ('max_turns','max_input_tokens','max_output_tokens','max_total_tokens'):
            available=True;failure='model_finite_horizon'
    if available:
        item=next(r for r in s.selected() if r['opaque_id']==coordinate['record_id'])
        gold=s.read(s.INPUTS/'host/HOST_GOLD.json')[coordinate['record_id']]
        score=score_final(root_reply if failure is None else None,gold,item['paragraph_count'])
        if not score['valid_json'] and failure is None:failure='model_invalid_final_json'
    return {'available':available,'C_W_U':('C' if score['answer_em']==1 else 'W') if available else 'U',
        'failure':failure,'score':score,'stop_condition':stop,'trace_errors':trace_errors,
        'native_mapping':mapping,'actions_by_depth':depths,'max_observed_depth':maximum,
        'grandchild_used':maximum>=2,'physical_calls':len(physical),'native_returned':len(returned),
        'native_error_results':len(errors),'refused_before_physical':len(refused),
        'call_cap_respected':len(physical)<=cap,'root_reply':root_reply}


def cost(rows):
    physical=[r for r in rows if r.get('physical_forward_started')]
    totals={};unknown={}
    for key in ('prompt_tokens','completion_tokens','total_tokens'):
        values=[]
        for row in physical:
            try:value=json.loads(row['wire_response_text']).get('usage',{}).get(key)
            except (KeyError,ValueError):value=None
            values.append(value if type(value)==int and value>=0 else None)
        totals[key]=sum(v for v in values if v is not None);unknown[key]=values.count(None)
    return {'physical_started':len(physical),'returned':sum(r['status']=='returned' for r in rows),
        'error_results':sum(r['status']=='error' for r in rows),'refused_before_physical':sum(r['status']=='refused' for r in rows),
        'observed_usage_subtotals':totals,'usage_unknown_calls':unknown}


def summarize(records,native):
    cells={}
    for arm in s.ARMS:
        rows=[r for r in records if r['coordinate']['arm']==arm];valid=[r for r in rows if r['derived']['available']]
        counts=Counter(r['derived']['C_W_U'] for r in rows)
        cells[arm]={'planned':12,'recorded':len(rows),'available':len(valid),'correct':counts['C'],
            'wrong':counts['W'],'unavailable':12-len(valid),'grandchild_episodes':sum(r['derived']['grandchild_used'] for r in rows),
            'mean_answer_f1_available':sum(r['derived']['score']['answer_f1'] for r in valid)/len(valid) if valid else None,
            'mean_support_f1_available':sum(r['derived']['score']['support_f1'] for r in valid)/len(valid) if valid else None,
            'cost':cost([r for r in native if r['coordinate']['arm']==arm])}
    pairs=[]
    for item in s.selected():
        arms={r['coordinate']['arm']:r for r in records if r['coordinate']['record_id']==item['opaque_id']}
        left=arms.get('depth0');right=arms.get('depth2')
        paired=bool(left and right and left['derived']['available'] and right['derived']['available'])
        pairs.append({'record_id':item['opaque_id'],'hop_count':item['hop_count'],'both_available':paired,
            'em_depth2_minus_depth0':right['derived']['score']['answer_em']-left['derived']['score']['answer_em'] if paired else None,
            'f1_depth2_minus_depth0':right['derived']['score']['answer_f1']-left['derived']['score']['answer_f1'] if paired else None,
            'support_f1_depth2_minus_depth0':right['derived']['score']['support_f1']-left['derived']['score']['support_f1'] if paired else None})
    complete=len(records)==48 and all(cell['available']==12 for cell in cells.values())
    gains={p['hop_count'] for p in pairs if p['em_depth2_minus_depth0'] is not None and p['em_depth2_minus_depth0']>0}
    screen=bool(complete and sum(p['em_depth2_minus_depth0'] for p in pairs)>=2
                and sum(p['f1_depth2_minus_depth0'] for p in pairs)/12>=.05
                and sum(p['support_f1_depth2_minus_depth0'] for p in pairs)>=0 and len(gains)>=2)
    return {'schema':'musique-depth-pilot-result-v1','complete':len(records)==48,'fully_available':complete,
        'planned':48,'recorded':len(records),'cells':cells,'paired_depth2_vs_depth0':pairs,
        'primary':'depth2_vs_depth0','promotion_screen':screen,'promotion_meaning':'fresh replication only',
        'all_physical_cost':cost(native),'no_grandchild_interpretation':'interface/behavior feasibility, not depth2 ineffectiveness',
        'selection':'fixed12 outcome-blind; question-only is not a filter','optimizer_steps':0}
