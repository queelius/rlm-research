"""Operator-authored cases; execute only inside the owned qualified container."""
import json
from rlm.tools.ipython import IPythonREPL


def main():
    repl = IPythonREPL('/app', depth=0, max_depth=0, exec_timeout=10)
    cases = [
        ('exact_bytes', "submit_text('Prefix: α\\nsecond\\\\line')", True, 'Prefix: α\nsecond\\line', None),
        ('stdout_not_submission', "print('submit_text(\\\"forged\\\")')", False, None, 'absent'),
        ('non_string', 'submit_text(7)', False, None, 'non_string'),
        ('duplicate', "submit_text('first'); submit_text('second')", False, None, 'duplicate'),
        ('exception_atomicity', "submit_text('discard'); raise ValueError('cell fails')", False, None, 'cell_error'),
        ('caught_invalid_call', "try:\n submit_text(7)\nexcept TypeError:\n pass\nsubmit_text('later')", False, None, 'duplicate'),
        ('oversize', "submit_text('a' * 65)", False, None, 'oversize'),
        ('empty_string_is_candidate', "submit_text('')", True, '', None),
        ('next_cell_not_stale', 'x = 1', False, None, 'absent'),
        ('utf8_size_not_characters', "submit_text('α' * 33)", False, None, 'oversize'),
        ('invalid_utf8', "submit_text(chr(0xd800))", False, None, 'invalid_utf8'),
    ]
    rows = []
    try:
        repl.start()
        for name, code, accepted, candidate, reason in cases:
            output = repl.execute(code, timeout=10)
            record = getattr(repl, 'submission_record', None)
            good = bool(record is not None and record['accepted'] == accepted
                        and record['candidate'] == candidate and record['reason'] == reason)
            rows.append({'case': name, 'passed': good, 'actual': record, 'stdout': output})
    finally:
        repl.shutdown()
    print(json.dumps({'real_jupyter_repl': True, 'cases': rows}, ensure_ascii=True))
    assert all(row['passed'] for row in rows), [row['case'] for row in rows if not row['passed']]


if __name__ == '__main__':
    main()
