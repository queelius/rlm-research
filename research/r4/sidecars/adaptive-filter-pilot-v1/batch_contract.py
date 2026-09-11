"""Public pure serialization/structural decoder. No model, selection or gold access."""
import json

LABELS = ('human being', 'location', 'abbreviation', 'entity',
          'description and abstract concept', 'numeric value')
DEFINITIONS = (
    "Classify the type of answer requested, not words mentioned in the question.\n"
    "human being: a person, an organization or group of people, or a person's role, "
    "title or description.\n"
    "location: a geographic place, including a city, country, state, mountain or other place.\n"
    "abbreviation: a shortened form, or the expanded wording represented by a shortened form.\n"
    "entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, "
    "events, substances, methods or synonymous terms.\n"
    "description and abstract concept: a definition, explanation, reason or manner of doing "
    "something, rather than a particular name or number.\n"
    "numeric value: a quantity, count, measurement, date, duration, rank or numerical code.\n"
)


def request_for(records):
    rows = [{'id': r['id'], 'text': r['text']} for r in records]
    if not rows or any(not isinstance(v, str) for r in rows for v in r.values()) or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('nonempty unique public records required')
    return ('Classify the type of answer requested by each question using these TREC definitions:\n'
            + DEFINITIONS + 'Return only one JSON object mapping every supplied id exactly once to one label.\n'
            'No missing or extra ids. Allowed labels: ' + json.dumps(LABELS, ensure_ascii=False, separators=(',', ':'))
            + '\nRecords: ' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')))


def strict_map(raw, ids):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError('duplicate key: ' + key)
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate requested IDs')
    result = json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
    if not isinstance(result, dict) or set(result) != set(ids):
        raise ValueError('map missing/unknown IDs or non-object')
    if any(not isinstance(value, str) or value not in LABELS for value in result.values()):
        raise ValueError('invalid label')
    return result
