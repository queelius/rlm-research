"""Pure supplied-map reduction. No query, metadata, filesystem, or gold access."""

LABELS = ('human being', 'location', 'abbreviation', 'entity',
          'description and abstract concept', 'numeric value')


def count_labels(labels, requested_ids, target):
    """Count target among unique requested IDs; invalid maps/coverage raise ValueError."""
    if not isinstance(labels, dict) or any(not isinstance(k, str) or v not in LABELS
                                           for k, v in labels.items()):
        raise ValueError('map must contain string IDs and exact category labels')
    if not isinstance(requested_ids, (list, tuple)) or any(not isinstance(i, str) for i in requested_ids):
        raise ValueError('requested_ids must be a list or tuple of strings')
    if len(set(requested_ids)) != len(requested_ids) or not set(requested_ids) <= labels.keys():
        raise ValueError('requested IDs must be unique and covered by supplied map')
    if target not in LABELS:
        raise ValueError('target must be an exact category label')
    return sum(labels[i] == target for i in requested_ids)
