import copy
import json
from pathlib import Path
import pytest

def test_primary_complete_wrong_label_is_semantic_error():
    from bg_protocol import score
    x=score('{"a":"entity","b":"location"}',['a','b'],{'a':'location','b':'location'},True)
    assert x['available'] and x['complete_map'] and x['strict_correct']==1
def test_duplicate_id_is_observed_invalid_not_null():
    from bg_protocol import score
    x=score('{"a":"entity","a":"location"}',['a'],{'a':'location'},True)
    assert x['available'] and not x['complete_map'] and x['strict_correct']==0
def test_missing_native_is_null():
    from bg_protocol import score
    assert score(None,['a'],{'a':'location'},False)['strict_correct'] is None
def test_extra_id_never_salvages_correct_subset():
    from bg_protocol import score
    x=score('{"a":"location","b":"entity"}',['a'],{'a':'location'},True)
    assert x['strict_correct']==0 and not x['complete_map']
def test_partition_preserves_every_public_record():
    from bg_protocol import partitions
    rows=[{'id':str(i),'text':'x'} for i in range(256)]
    assert list(map(len,partitions(rows,'W')))==[100,100,56]
    assert list(map(len,partitions(rows,'S')))==[16]*16
    assert sum(partitions(rows,'S'),[])==rows
