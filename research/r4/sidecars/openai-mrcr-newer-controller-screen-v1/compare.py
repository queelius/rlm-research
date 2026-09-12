"""Fixed8 paired contexts; parsed primary and untouched-token diagnostic kept distinct."""
from pathlib import Path
import study as s


def report(output=s.ATTEMPT):
    arms={arm:{s.read(p)['coordinate']['record_id']:s.read(p) for p in (output/arm/'science/episodes').glob('*.json')}
          for arm in s.ARMS}
    pairs=[]
    for row in s.selected():
        values={arm:arms[arm].get(row['id']) for arm in s.ARMS}
        d={arm:value['derived'] if value else None for arm,value in values.items()}
        paired_known=all(value is not None and value['known_model_outcome'] for value in d.values())
        old,new=d['qwen3'],d['qwen35']
        exact={arm:(value['raw_exact'] is True) if value and value['known_model_outcome'] else None for arm,value in d.items()}
        pairs.append({'record_id':row['id'],'paired_known':paired_known,
            'terminal_classes':{arm:value['terminal_class'] if value else 'unattempted' for arm,value in d.items()},
            'parsed_final_exact':exact,
            'new_win':paired_known and exact['qwen35'] and not exact['qwen3'],
            'new_loss':paired_known and exact['qwen3'] and not exact['qwen35'],
            'first_actions':{arm:value['first_action'] if value else None for arm,value in d.items()},
            'observed_selection':{arm:value['observed_selection'] if value else None for arm,value in d.items()},
            'final_fidelity':{arm:value['final_text_fidelity'] if value else None for arm,value in d.items()}})
    results={arm:s.read(output/arm/'science/RESULT.json') if (output/arm/'science/RESULT.json').exists() else None for arm in s.ARMS}
    return {'schema':'released-controller-screen-paired-v1','planned_paired_contexts':8,
        'both_known':sum(p['paired_known'] for p in pairs),'new_wins':sum(p['new_win'] for p in pairs),
        'new_losses':sum(p['new_loss'] for p in pairs),'arms':results,'pairs':pairs,
        'model_order':['qwen3','qwen35'],'root_turns_per_episode':2,'children':0,
        'primary':'original harness root_reply after native parsing and harness stripping; exact string and unchanged official scorer',
        'raw_token_fidelity_is_separate_diagnostic':True,
        'no_independent16_item_inference':True,'no_new_data_or_recursion_claim':True,
        'model_package_template_parser_effects_not_weight_only':True}


if __name__=='__main__':
    value=report();s.write_x(s.ATTEMPT/'PAIRED.json',value)
    print({k:value[k] for k in ('planned_paired_contexts','both_known','new_wins','new_losses')})
