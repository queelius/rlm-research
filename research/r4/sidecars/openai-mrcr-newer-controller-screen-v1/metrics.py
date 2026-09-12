"""Host-only terminal and observed-selection diagnostics; never execute generated code."""
import ast
from collections import Counter
import json
from pathlib import Path
import study as s


def terminal_status(stop,ok,errors,mapped,reply):
    if errors or not mapped:return 'unavailable_provider_or_mapping'
    if stop in ('max_turns','max_input_tokens','max_output_tokens','max_total_tokens'):
        return 'model_no_final_within_two_turns'
    if stop!='agent_completed':return 'unavailable_unknown_stop'
    return 'valid_final' if ok and isinstance(reply,str) and reply.strip() else 'model_invalid_final'


def observation_inventory(observations,messages,gold):
    target=gold['desired_msg_index'];assert messages[target]['role']=='user' and messages[target+1]['role']=='assistant'
    target_request=messages[target]['content'].strip().casefold()
    matching=[i for i,m in enumerate(messages[:-1]) if m['role']=='user' and m['content'].strip().casefold()==target_request]
    observed=[i for i,m in enumerate(messages[:-1]) if m['content'] and any(m['content'] in o for o in observations)]
    # Exact full-content inclusion establishes observation, not the program's intended lookup.
    return {'target_user_index':target,'target_assistant_index':target+1,
        'target_ordinal':matching.index(target)+1,'matching_user_indices':matching,
        'matching_message_indices':observed,'matching_message_roles':[messages[i]['role'] for i in observed],
        'target_assistant_observed':target+1 in observed,
        'unique_target_only':observed==[target+1],
        'multiple_assistant_responses_observed':sum(messages[i]['role']=='assistant' for i in observed)>1,
        'interpretation':'full-content inclusion only; broad dump is not faithful selection; no code re-execution'}


def first_action(row,arm):
    from jsonschema import Draft202012Validator
    if row is None:return {'available':False,'schema_correct':None}
    payload=row['response'];ids=payload['tokens']['completion_ids']
    parsed=s.renderer(arm).parse_response(ids,tools=row['body'].get('tools'))
    calls=parsed.tool_calls;values=[]
    for call in calls:
        arguments=call.arguments
        schema=next((tool['function']['parameters'] for tool in row['body'].get('tools',[])
                     if tool['function']['name']==call.name),None)
        valid=bool(str(call.status.value)=='ok' and call.name=='ipython' and isinstance(arguments,dict)
                   and schema is not None and Draft202012Validator(schema).is_valid(arguments))
        code=arguments.get('code') if isinstance(arguments,dict) else None
        try:ast.parse(code) if isinstance(code,str) else (_ for _ in ()).throw(ValueError())
        except (SyntaxError,ValueError,TypeError):syntax=False
        else:syntax=True
        values.append({'name':call.name,'status':str(call.status.value),'schema_correct':valid,
                       'code':code,'python_parseable':syntax})
    attempted='<tool_call>' in s.tokenizer(arm).decode(ids,skip_special_tokens=False)
    return {'available':True,'kind':'tool' if calls or attempted else 'terminal_text',
        'schema_correct':all(v['schema_correct'] for v in values) if values else (False if attempted else None),
        'calls':values,'nonempty_text':bool(parsed.content and parsed.content.strip())}


def inspect(raw,coordinate,native):
    traces=raw.get('traces') or [];trace=traces[0] if len(traces)==1 else {}
    errors=[*raw.get('errors',[]),*(e for t in traces for e in t.get('errors',[]))]
    rows=[r for r in native if r['coordinate_id']==coordinate['id']]
    returned=[r for r in rows if r['status']=='returned']
    mapping=s.causal().map_trace(trace,rows,max_actions=2)
    first=min(returned,key=lambda x:x['index']) if returned else None
    expected=s.read(s.PREFIX_FILE)[coordinate['id']]['token_ids']
    prefix=first is not None and first['response']['tokens']['prompt_ids']==expected
    mapped=bool(mapping['complete'] and mapping['child_actions']==0 and prefix)
    gold=s.read(s.INPUTS/'HOST_GOLD.json')[coordinate['record_id']]
    reply=trace.get('root_reply');status=terminal_status(trace.get('stop_condition'),bool(raw.get('ok')),errors,mapped,reply)
    nodes=trace.get('nodes') or []
    observations=[(n.get('message') or {}).get('content') or '' for n in nodes if (n.get('message') or {}).get('role')=='tool']
    observations=[x if isinstance(x,str) else json.dumps(x) for x in observations]
    source=next(x for x in s.selected() if x['id']==coordinate['record_id'])
    messages=s.read(source['prompt_json_path'])
    valid=status=='valid_final';known=not status.startswith('unavailable')
    last=max(returned,key=lambda x:x['index']) if returned else None
    raw_final=None
    if last is not None and trace.get('stop_condition')=='agent_completed':
        final_ids=list(last['response']['tokens']['completion_ids'])
        stops=set(s.renderer(coordinate['arm']).get_stop_token_ids())
        while final_ids and final_ids[-1] in stops:final_ids.pop()
        raw_final=s.tokenizer(coordinate['arm']).decode(final_ids,skip_special_tokens=False)
    native_final=(last['response'].get('message') or {}).get('content') if last is not None else None
    fidelity={'raw_model_final_stop_tokens_removed':raw_final,
        'parsed_native_final':native_final,'original_harness_final':reply,
        'raw_model_final_exact':raw_final==gold['answer'] if raw_final is not None else None,
        'raw_model_final_official_score':s.official_grade()(raw_final,gold['answer'],gold['random_string_to_prepend']) if raw_final is not None else None,
        'raw_equals_native_parsed':raw_final==native_final if raw_final is not None else None,
        'native_parsed_equals_harness':native_final==reply if isinstance(native_final,str) else None,
        'raw_to_native_difference_is_exactly_strip':raw_final!=native_final and raw_final.strip()==native_final if raw_final is not None else None,
        'native_to_harness_difference_is_exactly_strip':native_final!=reply and native_final.strip()==reply if isinstance(native_final,str) else None,
        'raw_utf8_bytes':len(raw_final.encode()) if raw_final is not None else None,
        'parsed_utf8_bytes':len(native_final.encode()) if isinstance(native_final,str) else None,
        'harness_utf8_bytes':len(reply.encode()) if isinstance(reply,str) else None,
        'diagnostic_only_no_primary_replacement':True,
        'decode_rule':'remove only trailing renderer stop-token IDs; decode skip_special_tokens=False; never strip or repair'}
    return {'terminal_class':status,'known_model_outcome':known,'valid_terminal':valid,
        'raw_exact':reply==gold['answer'] if valid else None,
        'official_score':s.official_grade()(reply,gold['answer'],gold['random_string_to_prepend']) if valid else None,
        'root_reply':reply,'stop_condition':trace.get('stop_condition'),'error_types':[e.get('type') for e in errors],
        'final_text_fidelity':fidelity,
        'initial_prefix_verified':prefix,'causal_mapping':mapping,
        'root_actions_returned':mapping['root_actions'],'child_actions_returned':mapping['child_actions'],
        'first_action':first_action(first,coordinate['arm']),
        'observed_selection':observation_inventory(observations,messages,gold),
        'observation_utf8_bytes':sum(len(x.encode()) for x in observations),
        'observation_tokens':sum(len(s.tokenizer(coordinate['arm']).encode(x,add_special_tokens=False)) for x in observations),
        'physical_started':sum(r.get('physical_forward_started',False) for r in rows),
        'returned':len(returned),'provider_error_results':sum(r['status']=='error' for r in rows),
        'pretransport_refusals':sum(r['status']=='refused' for r in rows),
        'prompt_tokens_observed_subtotal':sum(len(r['response']['tokens']['prompt_ids']) for r in returned),
        'completion_tokens_observed_subtotal':sum(len(r['response']['tokens']['completion_ids']) for r in returned),
        'usage_unknown_physical_calls':sum(r.get('physical_forward_started',False) and r['status']!='returned' for r in rows)}


def summarize(records,arm):
    rows=[r['derived'] for r in records];valid=[r for r in rows if r['valid_terminal']]
    return {'arm':arm,'planned_episodes':8,'recorded':len(records),'unattempted':8-len(records),
        'terminal_classes':dict(Counter(r['terminal_class'] for r in rows)),
        'valid_terminals':len(valid),'raw_exact_correct':sum(r['raw_exact'] for r in valid),
        'official_score_sum_valid':sum(r['official_score'] for r in valid),
        'first_action_schema_correct':sum(r['first_action'].get('schema_correct') is True for r in rows),
        'unique_target_assistant_observed':sum(r['observed_selection']['unique_target_only'] for r in rows),
        'complete_inventory':len(records)==8,
        'all_known_model_outcomes':len(records)==8 and all(r['known_model_outcome'] for r in rows),
        'cost':{k:sum(r[k] for r in rows) for k in ('physical_started','returned','provider_error_results',
            'pretransport_refusals','prompt_tokens_observed_subtotal','completion_tokens_observed_subtotal',
            'usage_unknown_physical_calls','observation_utf8_bytes','observation_tokens')},
        'unit':'8 paired contexts; two-turn package usability, not independent16 outcomes or recursive learning'}
