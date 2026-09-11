"""Three explicit immutable root lineages; the child never changes."""
from pathlib import Path
import study as s

RL_ROUND = s.ADAPTIVE / 'outputs/attempt-001/round-07'
RL_STOP = s.ADAPTIVE / 'outputs/attempt-001/STOP-19319d28dd474bc2bf06b366e991b5dd.json'
RL_PINS = {RL_ROUND / 'COMMIT.json': '2a89e8e2af9e79e550a1c0d2b87c3f633a4666af128fabe8a7be4071cc5a947b',
           RL_ROUND / 'GENERATION.json': '2fac5e68b9d80c5f6d0c2485c21564ba8187a3da969fb672e8330c2b90018df1',
           RL_ROUND / 'training/RESULT.json': 'b43199b1326abdf8706b79c335b1288215198fb8b9332f348943fd6afb4400f1',
           RL_STOP: 'ecd1c7f4221ae83017b748c3b7ad75129eadeb53df9073b78f94efbd2a296de2'}


def training_source(arm):
    return {'baseline': s.CONTROL, 'success_sft': s.ROOT / 'outputs/attempt-001/training',
            'rl7': RL_ROUND / 'training'}[arm]


def rl7_selected():
    for path, expected in RL_PINS.items():
        s.check(path, expected)
    commit = s.read(RL_ROUND / 'COMMIT.json')
    generation = s.read(RL_ROUND / 'GENERATION.json')
    if commit['generation'] != generation or generation['round'] != 7 or generation['fixed_child_sha256'] != s.CHILD_SHA:
        raise ValueError('not the exact fixed-child RL7 generation')
    common_path = s.SIDE / 'root-rlvr-campaign-v1/campaign_common.py'
    common = s.load('success_exact_rl_checkpoint_proof', common_path, '17e888550668638673fa725c6a580b7580b6abd975bd27f69b8be7ad628800ea')
    policy = common.checkpoint_policy(RL_ROUND / 'training', generation)
    if (policy != commit['policy'] or policy != s.read(RL_ROUND / 'training/RESULT.json')['policy']
            or policy['adapter_sha256'] != '809fc46ed50d36c5e61b2e8ae785ae84083b509fcb8bdd3b1914eaca3c0c842a'
            or policy['state_sha256'] != commit['checkpoint_state_sha256']):
        raise ValueError('last-saved RL7 weight/state closure changed')
    return {**policy, 'checkpoint': policy['path']}


def selected(arm):
    if arm == 'baseline':
        return s.control_selected()
    if arm == 'rl7':
        return rl7_selected()
    if arm != 'success_sft':
        raise ValueError('unknown exact arm')
    directory = training_source(arm)
    result = s.read(directory / 'RESULT.json')
    chosen = result['selected']
    path = directory / 'checkpoint-0008'
    if (not result['complete'] or result['optimizer_steps'] != 8 or chosen['step'] != 8
            or chosen['checkpoint'] != str(path) or result['identity'] != s.verify()['identity']
            or result['starting_adapter_sha256'] != s.CONTROL_SHA or not result['fresh_optimizer']
            or result['child_loaded'] or result['child_updated']
            or (result['episode_exposures'], result['root_turn_exposures'], result['target_token_exposures']) != (216, 912, 122048)
            or s.read(directory / 'SELECTION.json') != chosen):
        raise ValueError('not the exact complete fixed-final8 imitation result')
    s.check(path / 'state.json', chosen['state_sha256'])
    state = s.read(path / 'state.json')
    if (state['identity'] != result['identity'] or state['corpus_sha256'] != s.sha(s.ROOT / 'prepared/EPISODES.json')
            or (state['step'], state['epoch'], state['cursor']) != (8, 8, 0)
            or state['files_sha256'] != result['files_sha256']):
        raise ValueError('final8 full-pass state differs')
    for name, expected in state['files_sha256'].items():
        if Path(name).name != name:
            raise ValueError('invalid checkpoint member')
        s.check(path / name, expected)
    if (chosen['adapter_sha256'] != state['files_sha256']['adapter_model.safetensors']
            or chosen['config_sha256'] != state['files_sha256']['adapter_config.json']):
        raise ValueError('final8 selected files differ')
    return chosen


def binding(arm, chosen):
    value = s.stack().native.initial_binding()
    value['models'].pop(value['role_map']['root'])
    alias = 'strict-rlm-qwen3-4b-root-success-study-' + arm.replace('_', '-') + '-v1'
    model = {'path': chosen['checkpoint'], 'adapter_sha256': chosen['adapter_sha256'], 'config_sha256': chosen['config_sha256']}
    value['models'][alias] = model
    value['role_map']['root'] = alias
    state = s.read(Path(chosen['checkpoint']) / 'state.json')
    value['campaign_policy'] = {**model, 'step': chosen['step'], 'state_sha256': chosen['state_sha256'],
                               'optimizer_sha256': state['files_sha256']['optimizer.pt'], 'rng_sha256': state['files_sha256']['rng_state.pt']}
    value['campaign_id'] = s.ROOT.name
    value.pop('receipt_uptake_study', None)
    source = RL_ROUND / 'COMMIT.json' if arm == 'rl7' else training_source(arm) / 'SELECTION.json'
    value['selection_path'], value['selection_sha256'] = str(source), s.sha(source)
    value['selection_semantics'] = {'baseline': 'unchanged interface-SFT final4', 'success_sft': 'fixed complete-success SFT final8',
                                    'rl7': 'last-saved7 after no-mixed round8 STOP; not original final8 or validation selected'}[arm]
    value['success_trajectory_study'] = {'arm': arm, 'root_ready_sha256': s.sha(s.ROOT / 'READY.json'),
        'rl_original_stop_sha256': RL_PINS[RL_STOP] if arm == 'rl7' else None}
    if value['models'][value['fixed_child']]['adapter_sha256'] != s.CHILD_SHA:
        raise ValueError('fixed child changed')
    return value


def validate_descriptor(binding, descriptor, binding_sha):
    root = binding['models'][binding['role_map']['root']]
    if (descriptor['model_alias'] != binding['role_map']['root']
            or descriptor['adapter'] != {'path': root['path'], 'model_sha256': root['adapter_sha256'], 'config_sha256': root['config_sha256']}
            or descriptor['role_binding_sha256'] != binding_sha or descriptor['base_model']['manifest_sha256'] != s.BASE_SHA):
        raise ValueError('actual endpoint model/base/binding differs')
