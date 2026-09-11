# Does learned correspondence survive shuffled IDs without a grammar?

Proposal only, written before the indexed-SFT final readouts. No source changes, launch authority, or adaptive execution are implied. Revisit its priority after the running matched old/B/new comparison completes.

Coordination update: the parent has separately commissioned `leaf-indexed-grammar-transfer-v1`, a160-call old-versus-indexed-final, anonymous/indexed × free/schema comparison on six TREC and four fresh SST contexts. That is the active preparation decision. The96-call ID-regime design below is an alternative/later discriminator, **not another queued job**; avoid duplicating the commissioned grammar study.

## Why this is the remaining distinction

The completed anchor control shows strong old-model performance with indexed, schema-constrained outputs on two tasks. It does not show that grammar is unnecessary. The running SFT experiment trains and tests IDs that restart at `q0001` in each batch; these IDs are also position cues. A model can improve that contract without learning to preserve arbitrary record identity through reordering.

## Smallest informative follow-up

Use four64-sentence contexts from the next256 normalized-hash-ordered SST-2 validation groups, excluding the512 groups in the earlier sentiment and anchor studies. First verify that at least256 groups remain; otherwise record insufficiency without selecting by labels. Freeze the group manifest, prompts, seeds, and physical token IDs before any model call. Public-validation/pretraining/license caveats remain unchanged.

Compare the authenticated old child, fixed-final B, and fixed-final indexed child. For each, cross two ID regimes with free versus schema-constrained indexed output:

- Batch-local ascending IDs, matching the indexed training convention.
- Stable record IDs retained through an independently frozen shuffle, so ID number no longer reveals current input position.

Both regimes contain the same sentence order and labels. Only IDs change; all outputs remain ID→sentiment maps. Two fresh frozen sampling seeds give4 contexts ×2 seeds ×2 ID regimes ×2 output controls ×3 checkpoints =96 calls. Use the same native system/tools and sentiment definitions, temperature0.5, a common3,072-token cap, and an input-plus-cap8192 check. Exact schemas and unconstrained requests must differ only in the declared output-control field within each ID regime.

Primary measures are context-paired canonical accuracy and exact ID coverage, with first/last16 accuracy and all64-correct rate reported separately. Record actual generated tokens, elapsed time, and every physical request/prompt ID. Repeated seeds are nested in four source contexts; do not treat96 calls or repeated assignments as independent samples.

OneA100, at most four concurrent calls, two bounded service loads, a15-minute collection cap and30-minute total envelope including owned cleanup. Save each call immediately; no retries, output repair, checkpoint selection, or extra training. Existing checkpoints are bound by completed RESULT/selection/state/hash artifacts, not chosen on this transfer test.

## Decision criteria

These are prospective exploratory decision rules, not significance claims:

- **Promote a learned-transfer claim for further replication:** indexed SFT reaches at least90% free-output canonical accuracy with stable shuffled IDs, at least95% complete-ID coverage, improves by at least5 percentage points over both old and B under that same condition, and improves in every source context. Seek an independent dataset afterward; this is still SST public validation.
- **Revise toward grammar-supported correspondence:** schema remains strong but free outputs fail coverage or stable-ID accuracy; the useful contribution is the model–decoder contract, not grammar-independent capability.
- **Revise toward positional specialization:** local IDs work while stable shuffled IDs lose more than5 points under otherwise matched conditions. Test ID diversity during training before increasing training duration.
- **Retire the claim that indexed training is needed for this transfer setting:** old/B match the indexed checkpoint within the small study's descriptive uncertainty, especially if schema already solves the task. Keep the cheaper inference-time intervention as the working hypothesis.

Even a positive result would remain a component-level classification result. End-to-end RLM deployment requires a separately specified child-output contract and a paired root evaluation; silently substituting a dictionary-trained child into array-assuming root code would confound the experiment.

## Partial-result refinement: distinguish tool mode from missing semantics

The completed old-model fixed5 indexed readout later revealed98/98 tool-call responses, including96 parseable `ipython` envelopes and two unclosed envelopes. The emitted text was inspected only, never executed; no recovered labels replace primary scores. This makes tool-mode selection an additional concrete mechanism, not merely hypothetical ID-position confusion.

After the commissioned grammar study, a cheaper discriminator may be a matched old-model indexed request with versus without tool availability, using an explicitly consistent system contract. If plain JSON and strong label accuracy appear without training once tool use is unavailable, avoid attributing the original strict-zero score to missing classification knowledge. This would be a new declared harness ablation, not an offline repair of current outputs or a change to the running controls. Its priority depends on the completed grammar and three-weight results.
