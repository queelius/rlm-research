# Pre-inference receipt-format correction: use source-ID maps

Main decision September9,2026 at approximately06:24UTC, before parent acceptance
or any live receipt-study model call. Supersedes only the proposed array-of-objects
format in DESIGN_PROPOSAL.md/RECEIPT_IMPLEMENTATION_DECISION.md. No study outcomes
were inspected: none exists. The implementer is instructed not to mutate sealed
READY inputs if it has already published; use an additive version in that case.

Reason: the completed 368-control report provides decision-relevant shape evidence.
Old-child unconstrained tagged arrays were invalid in every padding cell (0/8 per
task/format), whereas free source-ID maps were valid12/12 on TREC,727/768 correct.
An object with id,label fields is not exactly the tested tag,label format, and
small batches may differ, but adopting the already successful simpler map is the
better exploratory default for an API that accepts text without a decoding grammar.

Both indexed-raw and receipt arms will use the SAME deterministic child prompt:
return a JSON object mapping each requested source ID to one caller-allowed label.
Receipt validation detects duplicate JSON keys, missing/extra IDs, invalid types
and labels, non-JSON constants, fences/truncation/prose; no repair or normalization.
Keep exact raw output and metadata, explicit requested-subset/source-byte binding,
and returned lexical key order. A valid mapping is order-independent; an invalid
one has labels_by_id=None. Semantic correctness is not certified by this receipt.

The three-arm72-episode plan, seeds, model choices, task content, score, optional
uptake, no-retry rule and budgets are unchanged. Repeat only focused parser and
small fake-broker runtime qualification affected by this choice. No broad tests or
new GPU smoke. Record the existing local qualification as superseded-format CPU
evidence rather than silently calling it qualification of the new format.

This is the adaptive research loop: use completed evidence to improve the next
design before collection, while preserving the earlier proposal and qualification.
