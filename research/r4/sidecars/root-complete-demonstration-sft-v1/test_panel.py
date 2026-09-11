import copy
import importlib.util
from pathlib import Path


def test_selection_never_uses_labels_and_preserves_disjoint_strata():
    spec=importlib.util.spec_from_file_location('panel',Path(__file__).with_name('panel.py'))
    assert spec is not None and Path(spec.origin).exists(), 'panel implementation missing'
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    rows=[{'question_group_sha256':str(i),'coarse':'NUM'} for i in range(40)]
    first=module.choose(rows,{'0'},'train')
    changed=copy.deepcopy(rows)
    for r in changed:r['coarse']='HUM'
    second=module.choose(changed,{'0'},'train')
    assert [r['question_group_sha256'] for r in first]==[r['question_group_sha256'] for r in second]
    assert len(first)==32 and len({r['question_group_sha256'] for r in first})==32
    assert '0' not in {r['question_group_sha256'] for r in first}
