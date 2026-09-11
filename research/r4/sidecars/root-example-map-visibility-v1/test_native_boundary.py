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
        assert 'PRIVILEGED ORACLE TREATMENT' not in frozen['prompt']
        assert ('<supplied_labels_json>' in frozen['prompt']) == row['inline']
    c = public[0]
    task = s.task(c, prompts[0]['prompt'], 0, rows[0], b'{"q0001": "human being"}')
    assert task.data.dataset == 'root-example-map-visibility-v1'
    assert task.data.context_window_id == 98133000
    assert task.data.source_split == 'root-disjoint-helper-train'


def test_task_writes_exact_supplied_map_and_no_helper(monkeypatch):
    public = s.read(s.ROOT / 'inputs/PUBLIC.json')[0]
    payload = b'{"q0001": "numeric value"}'
    plain = s.task(public, 'cpu boundary', 0, {'id': 'cpu'}, payload)
    async def inherited_setup(self, trace, runtime):
        runtime.base_called = True
    monkeypatch.setattr(type(plain).__bases__[0], 'setup', inherited_setup)
    class Runtime:
        def __init__(self):
            self.files = {}
            self.base_called = False
        async def write(self, name, payload):
            self.files[name] = payload
    for example in (False, True):
        for inline in (False, True):
            task = s.task(public, 'cpu boundary', 0, dict(id='cpu', example=example, inline=inline), payload)
            runtime = Runtime()
            asyncio.run(task.setup(None, runtime))
            assert runtime.base_called
            assert runtime.files == {'labels.json': payload}
