# Distinguish source-identity cues from a changing position counter

Bounded exploratory control using the existing leaf-anchor-padding-control-v1
collector, scorer and owned single-adapter lifecycle through private frozen
imports. New namespace: sidecars/leaf-identity-counter-v1. No active source edits,
GPU calls, environment mutation, retries or acceptance by the preparation agent.

Question: when source IDs are randomized out of positional order, do matching
output IDs help more than equally structured, changing but task-irrelevant
position tags? This follows the completed meaningful-versus-constant result;
that result did not distinguish identity from ordinal bookkeeping.

## Frozen design to prepare

- Existing old child c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3,
  same pinned Qwen3-4B base/native sampler/lifecycle as padding128.
- Reuse the exact eight64-record contexts in padding128 (four TREC/four SST).
  They are exposed developmental groups, not newly acquired or untouched data.
  No record selection by label/outcome. Preserve original record/source provenance.
- Assign source IDs q0001..q0064 by a fresh deterministic random permutation per
  context, independent of labels and presentation position. Preserve each record's
  assigned ID through two independent frozen presentation permutations. A source
  ID therefore does not encode the displayed ordinal position.
- Three output formats, all ordered arrays of64 objects with keys tag then label:
  matching randomized source-ID tags; ordinal tags p0001..p0064 in displayed order;
  constant placeholder tag p0000. Ordinal/constant tags are disjoint from source IDs.
  Qualify token lengths of q/p tags before freezing; if q/p tokenization differs,
  choose another disjoint one-token prefix and record that pre-inference decision.
- The same ID-bearing source text/order and tools are used in all three arms at
  a context/permutation/seed coordinate. Only truthful output-tag instruction and
  exact grammar differ. Semantic target for every arm is the displayed record at
  that array position. No wrong-source-ID scoring or keyed-map ambiguity.
- Eight contexts × two permutations × two sampled seeds × three arms =96 calls.
  Derive seeds and permutations from new namespace/master981266001. Freeze all
  before inference and verify no collision with previous study seeds. Balance
  the six three-arm dispatch orders across coordinates as evenly as possible.
- Exact grammar only: prefixItems64, exact tags, canonical label enum, no extra
  keys or cardinality. Grammar never sees gold labels. Temperature0.5/full support,
 3072 output cap/8192 context, four workers,120-second HTTP timeout, zero retries.
  Proposed600-second collection,1200-second owned execution budget,1230 outer.
  Keep explicit cleanup reserve and actual observed clocks.

## Metrics and decision

Primary: matched meaningful-minus-ordinal semantic item accuracy by task and
source context, jointly valid calls only, alongside full planned strict scores.
Secondary: ordinal-minus-constant and meaningful-minus-constant; per-position
accuracy, per-call whole-batch and class-count-vector agreement, raw token/cache
cost, validity and lexical output key order. Unknown alignment is null; invalid
completed outputs can have strict0 but are not64 known semantic mistakes.

If ordinal matches meaningful but beats constant, revise toward positional
bookkeeping. If matching randomized source IDs outperform ordinal across groups,
pursue a more specific source-correspondence hypothesis. Either result remains
exploratory and does not prove an attention mechanism; prompt/grammar token content
still differs. Prefer this discriminator to another specialized SFT run now.

Use focused test-first checks for stable randomized IDs across presentations,
label-independent construction, complete96 grid and paired inputs, exact tag
semantics/cardinality, nulls and native schema/token compatibility. Reuse qualified
single-alias lifecycle; no scheduler implementation. Return READY, SPEC/input
hashes, exact argv and a concise preparation report beside this brief. Main reviews
and launches. CPU preparation cap about15minutes; report a concrete dependency
promptly rather than building broad infrastructure. No subagents.
