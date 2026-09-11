# Warm-start reference24 independent audit method

Status: frozen prospectively at `2026-09-10T00:15:21Z`, while the accepted job was waiting
behind MNLI and `sidecars/root-warmstart-reference-v1/outputs` contained zero files. The study
READY SHA-256 was `3b1cbbe962262114b7931034f5d5dc98e21ca3b050f108a66fdbb4d14bb328f1`
and its canonical identity was
`25de35614384ba6640f8c978ccd5318d71a379540ef94f908ac4ecc9d971b1a2`.

## Independence and prior exposure

I did not design, implement, qualify, select checkpoints for, or launch this study. I previously
performed the independent audit of the query-sensitive RL campaign and helped write its living
synthesis. That evidence motivated interest in calibration, but it did not alter this already fixed
study. Before freezing this method I read the study design, implementation, READY seal, input
receipts, and CPU qualification artifacts, but no science output. The four `readout-00` through
`readout-03` contexts and all 64 source records were already QSR/research exposed and child-SFT
exposed; this is a matched diagnostic on exposed contexts, not fresh-context confirmation.

## Fixed panel and estimands

There are 24 planned endpoints: three served root policies crossed with the same eight blocks,
using the same seed within each three-root block. The eight blocks occupy four dependent context
clusters. Gold answers are `[0,3,0,2,2,0,0,5]` in frozen block order: four zero and four nonzero.
The policies are `released_reference` (857 zero-effect inference adapter), `interface4` (efab
checkpoint 4), and `success8` (66c checkpoint 8), all with the fixed c32 child. The reference is a
served released-weight, mathematically zero-effect adapter; it is not evidence of bitwise bare-base
transport equivalence. Serial phase order is fixed as success8, released_reference, interface4, so
policy and phase/time order are confounded.

Primary descriptive estimands are strict whole-final correctness on all eight planned blocks per
policy and paired block-level differences against `released_reference`. I will report endpoint
availability and worst/best bounds separately. A returned, authenticated but wrong, malformed,
empty, tool-routed, or length-capped final is zero; an absent or unauthenticated final is NULL, not
zero. Pairwise wins/losses/ties require both endpoints available. Because four answers are zero and
zero is also the best constant (4/8), zero-gold and nonzero-gold results are always separate.
Context-cluster summaries and the eight paired blocks are descriptive; 24 endpoints are not treated
as 24 independent contexts.

## Input and native authentication

The audit independently recomputes each scalar from public records, host labels, and the structured
query. It checks unique row/block IDs, three roots per block, identical paired seeds/task coordinates,
the exact all-scope wording amendment, source/setup file hashes, and the frozen expected first native
messages, ordered tools, token IDs, and 2048-token root cap.

For outcomes, the parser joins request/result/physical evidence by native request ID. A final is
available only if its referenced request exists, is a depth-zero response for that coordinate,
has returned status, an authenticated stop/length branch, no tool call, and content identical to the
recorded root reply. It verifies at least one root first request against the frozen prompt, tools and
tokens. Any contradiction makes the endpoint unavailable while retaining the raw evidence. Raw files
and their hashes are preserved in the audit inventory.

## Mechanism and cost audit

No sampled code is executed or repaired. The parser extracts executed trace-node order, assistant
tool calls, tool observations, native routing depth, request/response status, and compact message
excerpts. I will manually classify only behavior evidenced by that sequence: public-file reads,
actual child acquisition, whether returned observations flow into later executed code/state, merging
across calls, scoped reduction, and observation-to-final flow. Code mentions or a child-call count
alone do not establish use. Conversely, an authentic literal-list strategy can be task success even
if it is not the hoped-for live-variable mechanism. Host gold is used only by the scorer/audit.

Costs report physical transport attempts, authenticated returned native completions, root/child
split, prompt/completion/total tokens when present, elapsed owner/phase/episode time, and NULL causes.
No provider billing or unobserved GPU work is inferred. Historical acquisition/training costs are
source provenance, not newly charged calls.

## Interpretation limits

This panel can indicate whether either served checkpoint changes behavior relative to the served
zero-effect reference under one common coding role, clarified all-scope wording, file-only records,
fixed child and exposed contexts. It cannot identify a checkpoint effect separately from fixed phase
order, establish transfer to fresh contexts, or prove equality to a bare-base service. Promotion
requires a nonzero-answer advantage with authentic evidence use and a fresh-context, phase-balanced
replication; zero-only gains or constant-compatible outputs are not acquisition/reduction evidence.

