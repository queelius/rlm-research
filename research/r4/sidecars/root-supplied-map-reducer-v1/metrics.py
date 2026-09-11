"""Host-only descriptive metrics; no sampled code is executed."""
import ast
import json
import re

from count_labels import LABELS, count_labels


def validate_map(text, ids):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    result = json.loads(text, object_pairs_hook=pairs)
    if not isinstance(result, dict) or set(result) != set(ids) or any(v not in LABELS for v in result.values()):
        raise ValueError('native map not exact full public-ID/category contract')
    return result


def score(trace, last_returned, gold):
    completed = bool(trace.get('is_completed'))
    reply = trace.get('root_reply')
    unavailable = (not last_returned or not completed or
                   (trace.get('ok') is False and trace.get('stop_condition') == 'error' and not reply))
    match = re.fullmatch(r'Answer: ([0-9]+)', reply) if isinstance(reply, str) else None
    return dict(reward=None if unavailable else int(bool(match) and int(match[1]) == gold),
                format=None if unavailable else bool(match), provider_unavailable=unavailable,
                completed=completed, reply=reply, empty=completed and reply == '')


def evidence(trace, labels, requested_ids, target):
    expected = count_labels(labels, requested_ids, target)
    match = re.fullmatch(r'Answer: ([0-9]+)', trace.get('root_reply') or '')
    programs, scalars = [], []
    for node in trace.get('nodes', []):
        message = node.get('message', {})
        if message.get('role') == 'tool':
            text = message.get('content')
            if isinstance(text, str) and re.fullmatch(r'\s*[0-9]+\s*', text):
                scalars.append(dict(node_index=node.get('index'), value=int(text)))
        for tool in message.get('tool_calls') or []:
            function = tool.get('function', tool)
            if function.get('name') != 'ipython':
                continue
            try:
                args = function.get('arguments', {})
                code = (json.loads(args) if isinstance(args, str) else args)['code']
                try:
                    tree = ast.parse(code)
                    valid = True
                    helper = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                                 and n.func.id == 'count_labels' for n in ast.walk(tree))
                    zip_risk = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                                   and n.func.id == 'zip' and len(n.args) >= 2
                                   and isinstance(n.args[1], ast.Name) for n in ast.walk(tree))
                except SyntaxError:
                    valid, helper, zip_risk = False, False, False
                programs.append(dict(node_index=node.get('index'), code=code,
                                     valid_python=valid, literal_helper_call=helper,
                                     bare_variable_zip_value_risk=zip_risk))
            except (TypeError, ValueError, KeyError):
                programs.append(dict(node_index=node.get('index'), valid_python=False))
    return dict(supplied_map_count=expected, scoped_coverage=len(set(requested_ids) & labels.keys()),
                requested_ids=requested_ids, supplied_ids=sorted(labels),
                final_map_consistent=None if not match else int(match[1]) == expected,
                integer_tool_observations=scalars,
                matching_integer_tool_observation=any(r['value'] == expected for r in scalars),
                programs=programs, actual_map_consistent_reduction=None,
                reduction_audit_status='manual code/actual observation audit required; no host execution')


def usage(records):
    result = dict(calls=len(records), child_requests=sum(r['depth'] > 0 for r in records))
    for key in ('prompt_tokens', 'completion_tokens', 'cached_input_tokens', 'cost'):
        values = [r.get('response', {}).get('usage', {}).get(key) for r in records]
        known = [v for v in values if isinstance(v, (int, float))]
        result[key] = dict(known_calls=len(known), sum_known=sum(known),
                           sum_all=sum(known) if len(known) == len(values) else None)
    return result
