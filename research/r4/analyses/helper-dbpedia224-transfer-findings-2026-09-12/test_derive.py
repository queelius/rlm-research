import importlib.util
from pathlib import Path


def test_recomputed_pairs_distinguish_wrong_label_churn_from_gain():
    path = Path(__file__).with_name('derive.py')
    assert path.exists(), 'synthesis not implemented yet'
    spec = importlib.util.spec_from_file_location('dbpedia_synthesis_fixture', path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    value = m.effects({'a': 'X', 'b': 'A', 'c': 'B'}, {'a': 'Y', 'b': 'X', 'c': 'A'},
                      {'a': 'A', 'b': 'A', 'c': 'A'})
    assert value['wins'] == 1 and value['losses'] == 1
    assert value['changed_labels'] == 3 and value['wrong_to_different_wrong'] == 1
