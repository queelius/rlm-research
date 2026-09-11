"""Existing native renderer/task with a recording file boundary; no containers/models."""
import asyncio
import json

import study as s


def test_actual_native_prompt_and_new_panel_metadata():
    rows = s.read(s.ROOT / 'inputs/PLAN.json')
    prompts = s.read(s.ROOT / 'inputs/PROMPTS.json')
    public = s.read(s.ROOT / 'inputs/PUBLIC.json')
    template = s.read(s.ROOT / 'inputs/NATIVE_TEMPLATE.json')
    renderer = s.stack().native.renderer()
    assert len(rows) == len(prompts) == 32
    assert len({r['id'] for r in rows}) == 32
    assert len({r['seed'] for r in rows}) == 8
    for row, frozen in zip(rows, prompts):
        actual = renderer.render([template['system'], {'role': 'user', 'content': frozen['prompt']}],
                                 tools=json.loads(template['tools_ordered_json']), add_generation_prompt=True)
        assert actual.token_ids == frozen['token_ids']
        assert 'PRIVILEGED ORACLE TREATMENT' in frozen['prompt'] if row['map_source'] == 'dataset_oracle' else 'PRIVILEGED ORACLE TREATMENT' not in frozen['prompt']
    c = public[0]
    task = s.task(c, prompts[0]['prompt'], 0, rows[0], {'q0001': 'human being'})
    assert task.data.dataset == 'root-supplied-map-reducer-v1'
    assert task.data.context_window_id == 98133000
    assert task.data.source_split == 'root-disjoint-helper-train'


def test_task_writes_exact_supplied_map_and_helper_only_in_assisted_arm(monkeypatch):
    public = s.read(s.ROOT / 'inputs/PUBLIC.json')[0]
    labels = {'q0001': 'numeric value'}
    plain = s.task(public, 'cpu boundary', 0, {'id': 'cpu', 'reducer': False}, labels)
    # The inherited setup owns native context/runtime setup and is already qualified.
    # Replace only that external boundary; exercise this task's real file injection.
    async def inherited_setup(self, trace, runtime):
        runtime.base_called = True
    monkeypatch.setattr(type(plain).__bases__[0], 'setup', inherited_setup)

    class Runtime:
        def __init__(self):
            self.files = {}
            self.base_called = False

        async def write(self, name, payload):
            self.files[name] = payload

    for assisted in (False, True):
        task = s.task(public, 'cpu boundary', 0, {'id': 'cpu', 'reducer': assisted}, labels)
        runtime = Runtime()
        asyncio.run(task.setup(None, runtime))
        assert runtime.base_called
        assert json.loads(runtime.files['labels.json']) == labels
        assert set(runtime.files) == ({'labels.json', 'count_labels.py'} if assisted else {'labels.json'})
        if assisted:
            assert runtime.files['count_labels.py'] == (s.ROOT / 'count_labels.py').read_bytes()
