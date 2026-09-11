"""Reuse MAIN's existing CPU-qualified allocation5780 stack adaptation only."""
import sys
import study as s

ROOT = s.ROOT.parent / 'runtime-an27-5780-v1'


def adapt():
    # Loading this source does not invoke its command-line lifecycle/main function.
    with s.source().aliases({}):
        previous = list(sys.path)
        sys.path.insert(0, str(ROOT))
        try:
            wrapper = s.load('clarity_accepted_runtime_wrapper', ROOT / 'study_wrapper.py',
                             'b7d1fcbb8788ebb10d4b1eb75f117c3b2e1d2cbbd9dc23ca94990eda521785f0')
        finally:
            sys.path[:] = previous
    wrapper.verify_runtime()
    mapping = s.read(s.ROOT / 'SOURCE_PATH_MAP.json')
    if s.sha(mapping['runtime_target']) != mapping['sha256']:
        raise ValueError('qualified runtime supervisor bytes differ')
    wrapper.adapt_stack(s.stack())
    return wrapper
