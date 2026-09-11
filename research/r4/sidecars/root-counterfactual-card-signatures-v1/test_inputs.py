"""All96 frozen input/source/seed pairs, no extra oracle task file."""
from collections import Counter
from pathlib import Path

def test_exact_gate_source_cells_seeds_original_prefix_and_counter_truths():
    assert (Path(__file__).parent/'inputs/EVALUATION_PLAN.json').exists(),'frozen96 inputs absent'
    import cf_study as s
    rows=s.read(s.ROOT/'inputs/FREE_PLAN.json');pairs=s.read(s.ROOT/'inputs/PAIRS.json');gold=s.read(s.ROOT/'inputs/HOST_GOLD.json');public={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')};gate={r['source_coordinate']['id']:r for r in s.read(s.GATE)['rows']};oldprompts=s.read(s.CT/'inputs/PROMPTS_ACCURATE.json');prompts=s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')
    assert len(rows)==96 and len(pairs)==24 and len(public)==16
    assert Counter(r['cell'] for r in rows)=={cell:24 for cell in s.CELLS}
    assert Counter(tuple(p['cells']) for p in pairs)=={tuple(s.CELLS[i:]+s.CELLS[:i]):6 for i in range(4)}
    assert len({r['parent_id'] for r in rows})==8 and len({r['seed'] for r in rows})==24
    for pair in pairs:
        pp=[r for r in rows if r['source_coordinate_id']==pair['source_coordinate_id']];assert len(pp)==4 and len({r['seed'] for r in pp})==1
        for r in pp:
            g=gate[r['source_coordinate_id']];ctx=public[r['context_id']];v=r['variant']
            assert s.answer(ctx['records'],gold[ctx['id']]['labels'],r)==(g['original_gold'] if v=='original' else g['chosen']['gold'])
            assert s.problem.enumerated_answer(ctx['records'],gold[ctx['id']]['labels'],r)==gold[ctx['id']]['answers'][r['family']]
            if v=='original' and r['card_arm']=='U':assert prompts[r['id']]['token_ids']==oldprompts[r['source_coordinate_id']]['token_ids']
            if v=='counterfactual':assert ctx['records']==g['counterfactual_records'] and r['threshold']==g['chosen']['threshold']
            assert len(prompts[r['id']]['token_ids'])+2048<=8192
    checks=s.read(s.ROOT/'CPU_INPUT_NATIVE.json')['rows'];assert len(checks)==96
    assert all(r['variant_files_correct'] and r['private_gold_invariant'] and r['no_extra_task_files'] for r in checks)
    assert s.read(s.ROOT/'inputs/EVALUATION_PLAN.json')['first_action']==[]
