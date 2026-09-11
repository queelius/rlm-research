"""Operator-authored IPython program; top-level await, never execute on host."""
import json
import re
from rlm.api import run as rlm
from batch_contract import request_for, strict_map

records = json.load(open('records.json'))
config = json.load(open('operator_config.json'))
query = open('query.txt').read()
match = re.fullmatch(r'How many records from user (u\d\d) ask for a numeric value\?', query)
if query == 'How many records in the entire file ask for a numeric value?':
    user = None
elif match:
    user = match.group(1)
else:
    raise ValueError('unrecognized frozen plain query')
selected = records if config['controller'] == 'all16' or user is None else [r for r in records if r['user'] == user]
labels = {}
transcript = {'controller_kind': 'operator', 'controller': config['controller'], 'query': query,
              'selected_ids': [r['id'] for r in selected], 'batches': [], 'answer': None, 'status': 'running'}
def save_transcript():
    with open('operator_result.json', 'w') as stream:
        json.dump(transcript, stream, ensure_ascii=False)
save_transcript()
for offset in range(0, len(selected), 16):
    batch = selected[offset:offset+16]
    request = request_for(batch)
    event = {'requested_ids': [r['id'] for r in batch], 'request': request, 'raw_answer': None}
    transcript['batches'].append(event)
    save_transcript()
    child = await rlm(request)
    event.update(raw_answer=child.answer, child_session_dir=str(child.session_dir), child_turns=child.turns)
    save_transcript()
    try:
        decoded = strict_map(child.answer, event['requested_ids'])
    except ValueError as error:
        transcript.update(status='child_protocol_failure', error=str(error))
        save_transcript()
        break
    event.update(returned_ids=list(decoded), labels_by_id=decoded)
    labels.update(decoded)
else:
    relevant = records if user is None else [r for r in records if r['user'] == user]
    count = sum(labels[r['id']] == 'numeric value' for r in relevant)
    transcript.update(answer=f'Answer: {count}', status='complete')
save_transcript()
print(json.dumps({'operator_status': transcript['status'], 'answer': transcript['answer']}))
