# Singleton inference-shape comparison

Fresh c32: {'correct': 229, 'available': 256, 'unavailable': 0, 'by_dataset': {'trec': 120, 'ag_news': 109}, 'cost': {'prompt_tokens': 202590, 'completion_tokens': 5031, 'cached_prompt_tokens': 185488}}.
Fresh reference step4: {'correct': 228, 'available': 256, 'unavailable': 0, 'by_dataset': {'trec': 120, 'ag_news': 108}, 'cost': {'prompt_tokens': 202590, 'completion_tokens': 5033, 'cached_prompt_tokens': 185488}}.
Paired: {'both_correct': 228, 'both_wrong': 27, 'reference_loss': 1}.
Fresh c32 versus old singleton: {'by_dataset': {'trec': {'both_correct': 120, 'both_wrong': 8}, 'ag_news': {'both_correct': 109, 'both_wrong': 19}}, 'changed': [], 'totals': {'both_correct': 229, 'both_wrong': 27}, 'old_correct': 229, 'new_correct': 229, 'identical_completion_ids': 256, 'source_result_sha256': '3bc4439aa93e1a8aa75c48f12ea3ac9a2e31e0a84c6ea674fc0f35f459ee4f08'}

Predeclared decision: {'rule': 'If singleton net gain is <3, do not claim size mismatch explains weak RL. If gain >=3 with no dataset harm, replicate on a fresh panel. Otherwise mixed/no promotion.', 'observed_dataset_deltas_reference_minus_c32': {'trec': 0, 'ag_news': -1}, 'observed_net': -1, 'decision': 'does_not_support_size_mismatch_explanation', 'learned_routing_claim': False}.

The exact64-call size-4 results are context only and are not pooled with this fresh singleton comparison. This is not a learned routing result or confirmatory generalization.
