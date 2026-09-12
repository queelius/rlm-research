"""Bounded four-question concurrency; checkpoint every native stage, never execute text."""
import concurrent.futures
import json
import os
from pathlib import Path
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import study


def bytes_x(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream: stream.write(data)


class Collector:
    def __init__(self, endpoint, output, deadline, tokenizer):
        self.endpoint, self.output, self.deadline, self.tokenizer = endpoint, Path(output), deadline, tokenizer
        self.lock, self.physical, self.request_ids = threading.Lock(), 0, set()
        self.rows = {(r['record_id'], r['role']): r for r in study.schedule()}

    def call(self, item, role, prompt=None, blocked=None):
        row = self.rows[item['record_id'], role]
        path = self.output / 'calls' / (row['call_id'] + '.json')
        value = {**row, 'physical_started': False, 'status': 'unattempted', 'transport_valid': False,
                 'text': None, 'usage': {}, 'started_epoch': None, 'ended_epoch': None,
                 'credentials_persisted': False, 'failure': blocked}
        if blocked is not None:
            value['status'] = 'dependency_unavailable'
        elif time.time() >= self.deadline:
            value['failure'] = 'science_deadline_before_dispatch'
        else:
            try:
                body = study.request(prompt, role, row['seed'], item['paragraph_count'], self.tokenizer)
                request_path = self.output / 'native' / (row['call_id'] + '-REQUEST.json')
                response_path = self.output / 'native' / (row['call_id'] + '-RESPONSE.json')
                prompt_path = self.output / 'prompts' / (row['call_id'] + '.json')
                payload = json.dumps(body, separators=(',', ':'), ensure_ascii=False).encode()
                bytes_x(request_path, payload)
                study.write_x(prompt_path, prompt)
                value.update(request_path=str(request_path), request_bytes_sha256=study.sha(request_path),
                             prompt_path=str(prompt_path), prompt_sha256=study.sha(prompt_path),
                             body_sha256=study.digest(body), prefix_tokens=len(body['token_ids']),
                             actual_prefix_plus_output=len(body['token_ids']) + row['max_tokens'])
                with self.lock:
                    if self.physical >= 132: raise ValueError('global physical admission cap exceeded')
                    if time.time() >= self.deadline: raise TimeoutError('science deadline before admission')
                    self.physical += 1
                    value.update(physical_started=True, started_epoch=time.time(), physical_index=self.physical,
                                 status='request_error')
                    study.write_x(self.output / 'starts' / (row['call_id'] + '.json'), value)
                credential = os.environ['STRICT_RLM_CALIBRATION_API_KEY']
                request = Request(self.endpoint, data=payload, method='POST', headers={
                    'content-type': 'application/json', 'authorization': 'Bearer ' + credential})
                try:
                    with urlopen(request, timeout=max(.01, min(180, self.deadline - time.time()))) as response:
                        raw, status = response.read(), response.status
                except HTTPError as error:
                    raw, status = error.read(), error.code
                bytes_x(response_path, raw)
                value.update(response_path=str(response_path), response_bytes_sha256=study.sha(response_path), http_status=status)
                decoded = study.decode(body, json.loads(raw, object_pairs_hook=study.official().strict_pairs), self.tokenizer)
                value.update(decoded)
                if status != 200:
                    value.update(transport_valid=False, failure='HTTP_non200')
                with self.lock:
                    rid = value.get('request_id')
                    if rid and rid in self.request_ids:
                        value.update(transport_valid=False, failure='duplicate_provider_request_id')
                    if rid: self.request_ids.add(rid)
                value['status'] = 'returned_valid' if value['transport_valid'] else 'returned_invalid'
            except Exception as error:
                value.update(failure=type(error).__name__, status='request_error' if value['physical_started'] else 'admission_error')
            finally:
                value['ended_epoch'] = time.time()
                value['wall_seconds'] = value['ended_epoch'] - value['started_epoch'] if value['started_epoch'] else None
        study.write_x(path, value)
        print(json.dumps({'record_id': item['record_id'], 'role': role, 'status': value['status'],
                          'physical_calls': self.physical, 'planned_calls': 132}), flush=True)
        return value

    def question(self, index, item):
        public = study.read(item['public_path'])
        assert study.sha(item['public_path']) == item['public_sha256']
        halves = study.partition(public, item['record_id'])
        calls = {}
        for side, role in enumerate(('report_left', 'report_right')):
            calls[role] = self.call(item, role, study.report_messages(public, halves, side))
        report_ok = all(calls[r]['transport_valid'] and calls[r]['text'].strip() for r in ('report_left', 'report_right'))
        reports = [calls[r]['text'] for r in ('report_left', 'report_right')] if report_ok else None
        calls['plan'] = self.call(item, 'plan', study.plan_messages(public, reports) if report_ok else None,
                                  blocked=None if report_ok else 'initial_report_unavailable_or_empty')
        queries = study.planning_queries(calls['plan'])
        planning = calls['plan']['text']
        parent_ok = report_ok and queries is not None
        parent_sha = study.digest(study.shared_parent(public, reports, planning)) if parent_ok else None
        # Balanced order over 12 rows, frozen before results; all controls retained.
        arms = list(study.ARMS[index % 4:] + study.ARMS[:index % 4])
        for arm in arms:
            if arm == 'full_source':
                calls[arm] = self.call(item, arm, study.messages(public, study.FINAL))
            elif arm == 'stop':
                calls[arm] = self.call(item, arm,
                    study.final_messages(public, reports, planning, None) if parent_ok else None,
                    blocked=None if parent_ok else 'shared_report_or_planner_unavailable')
            else:
                extra = []
                for side, label in enumerate(('left', 'right')):
                    role = arm + '_' + label
                    prompt = study.followup_messages(public, halves, reports, side,
                        queries[side] if arm == 'targeted' else None) if parent_ok else None
                    calls[role] = self.call(item, role, prompt,
                        blocked=None if parent_ok else 'shared_report_or_planner_unavailable')
                    extra.append(calls[role])
                extra_ok = parent_ok and all(v['transport_valid'] and v['text'].strip() for v in extra)
                calls[arm] = self.call(item, arm,
                    study.final_messages(public, reports, planning, [v['text'] for v in extra]) if extra_ok else None,
                    blocked=None if extra_ok else 'shared_or_additional_report_unavailable')
        value = {'record_id': item['record_id'], 'question_index': index, 'hop': item['hop_count'],
                 'shared_parent_sha256': parent_sha, 'branch_order': arms,
                 'selected_followup_questions': queries,
                 'calls': {r: v['call_id'] for r, v in calls.items()},
                 'all_planned_roles_accounted': set(calls) == set(study.roles())}
        study.write_x(self.output / 'questions' / (item['record_id'] + '.json'), value)
        return value


def execute(endpoint, output, deadline):
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
    study.official().metric_classes()  # Resolve scoped imports before threads start.
    collector = Collector(endpoint, output, deadline, tokenizer)
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        pending = {pool.submit(collector.question, index, item): item['record_id'] for index, item in enumerate(study.selected())}
        for future in concurrent.futures.as_completed(pending):
            try: future.result()
            except Exception as error: errors.append({'record_id': pending[future], 'type': type(error).__name__})
    return {'physical_started': collector.physical, 'errors': errors, 'GPU_model_loaded_in_collector': False}
