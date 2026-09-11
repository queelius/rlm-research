"""CPU-only frozen-input qualification; no model load or inference."""
import json
from pathlib import Path
import driver

root=Path(__file__).resolve().parent
recipe,prepared,manifest=driver.bound()
original=driver.data.read_json(driver.MIXED/'B/data.json')
tokenizer=driver.data.load_tokenizer()
for epoch,rows in enumerate(prepared['train']):
    groups=[g for r in rows for g in r['group_ids']]
    assert len(groups)==len(set(groups))==5065
    assert groups==[g for r in original['train'][epoch] for g in r['group_ids']]
    for row in rows:
        prefix=len(row['prompt_ids'])
        assert row['input_ids'][:prefix]==row['prompt_ids']
        assert row['labels'][:prefix]==[-100]*prefix
        assert row['labels'][prefix:]==row['input_ids'][prefix:]
        assert tokenizer.eos_token_id in row['labels'][prefix:]
        assert len(row['input_ids'])<=4096
        assert driver.score(row['target'],row)['correct']==[True]*len(row['gold'])
sets={split:{g for r in rows for g in r['group_ids']} for split,rows in [('train',prepared['train'][0]),('validation',prepared['validation']),('test',prepared['test'])]}
assert not (sets['train']&sets['validation'] or sets['train']&sets['test'] or sets['validation']&sets['test'])
for split,expected in [('validation',300),('test',489)]:
    for representation in ['anonymous','indexed']:
        rows=[r for r in prepared[split] if r['representation']==representation]
        assert sum(len(r['gold']) for r in rows)==expected
        assert all(driver.score(r['target'],r)['array_valid'] for r in rows)
assert manifest['optimizer_steps']==204
result={'schema':'indexed-sft-cpu-qualification-v1','status':'passed','manifest_identity':manifest['identity'],
        'source_hashes_authenticated':len(recipe['source_hashes']),'train_arrays':sum(len(e) for e in prepared['train']),
        'train_record_exposures':10130,'target_tokens':sum(e['target_tokens'] for e in manifest['epochs']),
        'max_training_length':max(e['max_length'] for e in manifest['epochs']),
        'long_max_prompt_tokens':max(len(r['prompt_ids']) for r in prepared['transfer64']),
        'long_max_prompt_plus_output_cap':max(len(r['prompt_ids'])+3072 for r in prepared['transfer64']),
        'final_generated_responses_per_weight':len(prepared['test'])+len(prepared['transfer64']),
        'planned_final_responses_three_weights':3*(len(prepared['test'])+len(prepared['transfer64'])),
        'no_gpu_or_model_forward':True,'qualifier_sha256':driver.data.file_hash(Path(__file__))}
driver.data.write_once(root/'QUALIFICATION.json',result)
print(json.dumps(result,sort_keys=True))
