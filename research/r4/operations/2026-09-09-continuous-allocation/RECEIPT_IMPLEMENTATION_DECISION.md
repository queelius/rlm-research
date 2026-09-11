# Execute optional receipts, with a contemporaneous unchanged-harness reference

Main decision at approximately06:12UTC, September9,2026. Implement approach2 in
DESIGN_PROPOSAL.md, plus one additional untreated reference arm. The proposal is
otherwise accepted. Standing user instructions delegate this decision; no pause
for approval is needed. New namespace: sidecars/root-receipt-ablation-v1.

Question: does an optional source-bound indexed helper improve whole-RLM exact
answers, and does an optional locally validated receipt add further benefit?
The practical comparison needs an unchanged-harness reference, not only two new
helpers that could both underperform the existing runtime.

Design: six existing exposed64-record transfer contexts × two target counts ×
two fresh seeds =24 coordinate triples. Three arms are unchanged historical
ordinary instruction, common indexed helper returning raw text/metadata, and
the identical helper plus optional receipt.72 total episodes, not72 independent
problems. Balance all six arm orders four times, freeze before inference. Root
historical step8 SHA473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd;
childc32de unchanged. No selection from the ongoing independent-seed run.

Primary incremental contrast: receipt versus indexed-raw. Key practical secondary:
indexed-raw versus unchanged, and receipt versus unchanged. Preserve strict final
score. The new helper does not force all-label classification, complete-context
coverage, decomposition, model retries or answer repair. Exact same selectedIDs,
query and vocabulary produce the same child prompt across helper arms. All raw
native calls and existing broker result fields remain intact. Local receipts are
gold-blind and unavailable mappings stay unavailable if parsing/validation fails.

Use seedmaster981267100 as proposed, audit collisions before freeze. CPU-only
runtime qualification may use a new owned rootless runtime and trusted fake
broker reply; no GPU service, model call or process signaling by implementer.
If a live smoke is necessary, declare one disjoint coordinate before main launch
and retain it outside the72 scored episodes. Do not silently add a pilot later.

Budget: proposed2100-second collection,2280-second work including service startup,
2400-second whole owned job and2430-second outer cap, ordinary cleanup grace.
Stop collection before the work deadline to preserve at least120 seconds cleanup.
No full source-closure rehash inside episode loops; separate terminal CPU analysis
from GPU ownership. Expected~15–25minutes, not a utilization guarantee.

Preparation is bounded to~25minutes; implement the smallest qualified stdlib helper,
task/collector adapters and pinned owned lifecycle. If actual integration exposes
a defect, fix that material seam without general runtime refactoring. The fallback
is the proposal's simpler optional parser, not a new framework or decoder.

Main will read/review exact source and focused qualification before accepting one
launch. Agent prepares only; immutable READY specifies source/input hashes, exact
argv, metrics, seeds, caps, failure accounting and artifact location. Preserve all
old sources and this frozen decision.
