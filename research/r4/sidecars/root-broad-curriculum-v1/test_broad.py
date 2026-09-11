"""Bounded generation, admission, fixed-final, and input regressions; CPU only."""
import importlib
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


def modules():
    assert (ROOT / 'campaign_common.py').exists(), 'broad16 adapter not implemented'
    return importlib.import_module('campaign_common'), importlib.import_module('prepare')


def test_generation_continues_across_eight_but_rejects_stale_or_seventeen():
    c, _ = modules()
    for step in (7, 8, 9, 16):
        policy = {'step':step-1, 'adapter_sha256':'cpu-fixture'}
        gen = c.generation_identity('fixture', step, policy, 'fresh-plan')
        assert c.check_generation(gen, policy, step-1) == step
        with pytest.raises(ValueError, match='optimizer'):
            c.check_generation(gen, policy, step-2)
    policy = {'step':16}
    with pytest.raises(ValueError):
        c.check_generation(c.generation_identity('f',17,policy,'p'),policy,16)


def test_only_complete_exact_twenty_four_coordinates_are_admitted():
    c, _ = modules()
    train = importlib.import_module('campaign_train')
    plans = [{'id':str(i),'task_name':str(i//8),'seed':i} for i in range(24)]
    rows = [{'episode_id':str(i),'task_id':str(i//8),'sample_seed':i,'split':'training'} for i in range(24)]
    manifest = {'recorded':24,'planned':24,'integrity_failures':[]}
    train.validate_collection(manifest,rows,plans)
    for bad in (rows[:-1], rows+[rows[0]], rows[:-1]+[rows[0]]):
        with pytest.raises(ValueError): train.validate_collection(manifest,bad,plans)
    bad = deepcopy(rows); bad[0]['sample_seed'] = 99
    with pytest.raises(ValueError): train.validate_collection(manifest,bad,plans)
    bad = deepcopy(rows); bad[0]['split'] = 'validation'
    with pytest.raises(ValueError): train.validate_collection(manifest,bad,plans)
    with pytest.raises(ValueError): train.validate_collection({**manifest,'recorded':32},rows,plans)


def test_candidate_cardinalities_seeds_and_final_pairing():
    c, prep = modules()
    inputs = prep.build_inputs()
    plans = inputs['PLANS.json']
    assert set(plans['training']) == set(map(str,range(1,17)))
    assert all(len(rows)==24 for rows in plans['training'].values())
    assert len(plans['validation'])==16
    assert len(plans['transfer_original'])==len(plans['transfer_final'])==48
    rows = [r for rs in plans['training'].values() for r in rs]+plans['validation']+plans['transfer_original']
    assert len(rows)==len({r['seed'] for r in rows})==448
    assert {r['seed'] for r in rows}.isdisjoint(prep.prior_seeds())
    assert [(r['task_name'],r['seed']) for r in plans['transfer_original']] == [(r['task_name'],r['seed']) for r in plans['transfer_final']]
    assert Counter(r['analysis_split'] for r in plans['transfer_final']) == {
        'transfer-composition':24,'transfer-size':12,'transfer-leaf-test-exposed':12}
    assert len(inputs['PUBLIC.json']['tasks'])==80
    assert len(inputs['PUBLIC.json']['contexts'])==47


def test_fixed_final_is_not_earliest_validation_maximum():
    c, _ = modules()
    campaign = importlib.import_module('campaign')
    policies = {i:{'step':i} for i in range(17)}
    vals = [{'step':i,'strict_successes':s,'planned':16,'admitted_outcomes':16}
            for i,s in [(0,3),(4,12),(8,12),(12,5),(16,6)]]
    decision = campaign.fixed_final_selection(policies,vals)
    assert decision['policy']['step']==decision['selected_step']==16
    assert decision['descriptive_earliest_max_validation_step']==4
    with pytest.raises(ValueError): campaign.fixed_final_selection({k:v for k,v in policies.items() if k!=16},vals)


def test_recipe_preserves_original_objective_and_precision():
    c,prep=modules()
    old=c.read(c.OLD/'RECIPE.json');new=prep.make_recipe()
    changed={'schema','training_seed','optimizer_steps','declared_at_utc','primary_policy','limitations','concurrency_amendment','caps'}
    assert {k:v for k,v in old.items() if k not in changed}=={k:v for k,v in new.items() if k not in changed}
    assert new['learning_rate']==5e-5 and new['optimizer_steps']==16 and new['caps']['global']==18000


def test_observed_process_exit_is_absent_but_other_errors_propagate():
    c, _ = modules()
    campaign = importlib.import_module('campaign')
    def gone(pid): raise ProcessLookupError('CPU vanished process fixture')
    def denied(pid): raise PermissionError('not absence')
    assert campaign.observer_fix.observe_or_absent(gone,123) is None
    with pytest.raises(PermissionError): campaign.observer_fix.observe_or_absent(denied,123)


def test_native_task_public_bytes_and_gold_boundary(monkeypatch):
    c,prep=modules()
    native=importlib.import_module('campaign_native')
    from oolong_prime_v1.taskset import _QUESTION_INSTRUCTION, _RLM_FILE_INSTRUCTION
    inputs=prep.build_inputs();original_read=c.read
    def read(path):
        path=Path(path)
        return inputs[path.name] if path.parent==c.ROOT/'inputs' and path.name in inputs else original_read(path)
    monkeypatch.setattr(c,'read',read)
    tasks=native.make_tasks()
    contexts={r['id']:r['text'] for r in inputs['PUBLIC.json']['contexts']}
    for row in inputs['PUBLIC.json']['tasks']:
        task=tasks[row['name']]
        assert task.data.context==contexts[row['context_id']]
        assert task.data.prompt==_QUESTION_INSTRUCTION+'\n\n'+_RLM_FILE_INSTRUCTION+'\n\nQuestion: '+row['question']
        rendered=native.capture.role.with_prompt(task,'sft_child').data.prompt
        assert 'negative' not in rendered and 'positive sentiment' not in rendered
        assert row['analysis_split'] not in rendered
    before={name:(t.data.prompt,t.data.context) for name,t in tasks.items()}
    for gold in inputs['HOST_GOLD.json'].values(): gold['answer']='[999999]'
    after=native.make_tasks()
    assert before=={name:(t.data.prompt,t.data.context) for name,t in after.items()}
