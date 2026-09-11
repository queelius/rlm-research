# Does an unrelated counter still help when its numbers cannot name the inputs?

Status: design proposal only, 2026-09-09. No implementation, frozen launch inputs,
acceptance, service, or model calls. Parent approval precedes CPU preparation;
the active broad16 root campaign has GPU priority.

## Why this comparison

The completed identity96 study found displayed-position correctness of
979/1024 meaningful versus 287/1024 ordinal versus 401/1024 constant on TREC,
and 960 versus 505 versus 591 on SST-2. However, an explicitly post-hoc audit
of the same ordinal responses found 859/1024 TREC and 953/1024 SST labels
agree with the source having the output tag's numeric suffix. All 32 calls
and all eight contexts improve under that alternative alignment. The original
primary scores remain unchanged. The counter was not mechanically neutral:
output p0001 could evoke input q0001 despite instructions to classify displayed
record 1. A prefix swap alone cannot remove that ambiguity.

This experiment asks whether meaningful identities outperform an unrelated
ordinal counter after removing shared numeric identities, and whether the
earlier failure depends on q/p lexical roles. It tests output correspondence in
one fixed child, not general reasoning or end-to-end RLM improvement.

## Smallest complete factorial

| Factor | Levels |
| --- | --- |
| Source prefix | q, p |
| Source numeric namespace | overlapping 0001–0064; disjoint randomized four-digit values |
| Output tag rule | meaningful source identity; displayed ordinal; constant |
| Reused material | eight frozen 64-record contexts: four TREC, four SST-2 |
| Repeated coordinates | two existing presentation permutations, two fresh sampled seeds |

Total: 2 × 2 × 3 × 8 × 2 × 2 = **384 calls**, 24,576 planned classifications.
Each task/condition has 16 calls and 1,024 planned classifications, but only four
source-context groups; seeds and permutations are nested repeated measurements.
Use the exact old child c32de checkpoint, not a newly chosen model. These public
contexts are already exposed; fresh seeds do not make the data untouched.

Reuse identity96 DATA.json records, stable source-rank assignment and both display
permutations. In the overlapping condition only the source prefix changes:
stable rank 1 remains numeric ID 0001 regardless of its displayed position.

For the disjoint condition, use master **981269001** and a named hash namespace
to select 64 unique values from 1000–9999 excluding last-three-digit suffixes
001–064. Rank eligible values by a digest of master, context identity and value;
assign that random ordering to the existing 64 stable source ranks. Labels never
enter this mapping. Do not sort selected values back into numerical order.
The mapping is shared across prefix swaps, permutations and seeds. This is not
1000 + rank, a positional offset, or a deliberately encoded numeric bijection.
Before freezing, assert there is no exact affine mapping, including modulo
10000, from stable rank or either displayed ordinal to the assigned values.
Any qualification failure returns to design review, not outcome-based remapping.

Meaningful tags equal the actual source IDs. Ordinal tags use the opposite
prefix and displayed positions 0001–0064. Constant tags use the opposite prefix
and 0000. Thus source q means ordinal p and source p means ordinal q. All three
arms classify the record at each displayed array position. There is no numeric
or suffix match from a disjoint source ID to any ordinal output tag; no nearest
number, hidden lookup, offset, or suffix repair is permitted in scoring.

## Keep physical comparisons interpretable

Within each prefix/namespace/context/permutation/seed triple, input records,
their source IDs, display order, generic system, tools, label definitions and
sampling are identical. Only the truthful tag-rule instruction and exact tag
grammar differ across arms. Full request bodies therefore are not identical.
Across prefix/namespace levels, only the specified source/output ID intervention
changes; preserve question text and display order byte-for-byte.

Use the pinned collector/scorer and array-of-objects grammar: exactly 64 objects,
tag before label, exact required tag at each array position, canonical task label
enum. No decoding repair or anonymous fallback. Before READY, qualify all 384
typed requests and grammars, render full physical prompt token IDs, and assert
prompt length + 3072 <= 8192. Record per-condition tag and prompt token lengths:
random four-digit strings may tokenize differently from low ordinals, so this
is not assumed token-compute matched. Record actual wire bodies and prompt IDs
at inference, not just the offline renderer's expectation.

Interleave the 12 prefix/namespace/arm conditions within each of 32 matched
context/permutation/seed coordinates. Use an outcome-independent cyclic balanced
condition order (each condition appears at each dispatch rank two or three times
over 32 coordinates), with paired reversed cycles to reduce order trends.
Freeze dispatch order and both new derived seeds after auditing master/seed
collisions against named existing studies. State that inventory's scope rather
than claiming a global collision proof. Use four workers on one warm alias;
retain dispatch and actual start/completion times separately.

## Prespecified readout and decision

Primary: paired meaningful-minus-ordinal displayed-position canonical accuracy
in the **disjoint** namespace, separately for TREC and SST, with both source
prefixes shown. Report strict whole-array validity, aligned-item availability,
correct/planned counts, and correct/alignable counts alongside it. Invalid
format is a strict failure, not 64 established semantic errors. Infrastructure
failures/unrun calls and unavailable alignment stay distinct/null.

Key interaction: (meaningful minus ordinal in disjoint) minus (meaningful minus
ordinal in overlap), within task and prefix. Also show each arm's absolute change;
a shrinking gap because meaningful degrades is not counter improvement. Constant
comparisons remain secondary. Report coordinate-level paired gains/losses and
context summaries; do not treat all repeated item observations as independent.

For **overlapping ordinal outputs only**, prospectively report both alignments:
(1) the instructed displayed-position gold, always primary; (2) source gold whose
numeric ID equals the emitted ordinal's number, ignoring the prefix solely for
this diagnostic. Never substitute (2) into primary accuracy or call it repaired
performance. In disjoint conditions that mapping has zero coverage and diagnostic
accuracy is unavailable, not forced to zero or obtained by a new rank lookup.
Retain per-call predicted/gold class-count vectors and their L1 distance before
aggregation: similar histograms alone do not establish correct correspondence.

- If ordinal improves when numbers are disjoint while meaningful stays strong,
  revise the previous result toward shared-ID interference, not a neutral-counter
  failure. A prefix interaction would identify additional lexical dependence.
- If meaningful still clearly exceeds both controls in disjoint conditions and
  across prefixes, prioritize a replicated identity-binding comparison on new
  contexts. This supports the tested representation, not an internal mechanism.
- If disjoint tags harm all arms or lexical/token-length differences dominate,
  the comparison is inconclusive about counter utility; qualify a narrower
  representation control before claiming identity-specific benefit.

## Resources and preparation boundary

Proposed unchanged decoding: temperature 0.5/full support, 3072 output tokens,
8192 model context, 120-second HTTP cap, zero retries, four workers. Expected
warm collection 20–25 minutes; collection cap 1800 seconds, owned inclusive
cap **2400 seconds** including service preparation and 120-second cleanup
reserve, parent outer cap 2430 seconds. Preserve every per-call checkpoint,
usage/cache-null field, error, alias, source identity and stage elapsed time.
Parent alone accepts/launches after broad16; no adaptive additional cells.

After design approval, CPU preparation should produce one new isolated sidecar,
reuse pinned lifecycle/collector code, and test only material seams: namespace
and permutation invariants; both scoring alignments on a reversed-ID fixture;
all actual grammars/full prompts/budgets and the 384-call dispatch crosswalk.
Publish immutable source/data/spec hashes and READY last. No training, model
downloads, environment mutation, or historical-source edits are needed.

## Evidence and exact reuse boundary

- [Identity96 design](../sidecars/leaf-identity-counter-v1/DESIGN.md) and
  [frozen records/permutations](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/leaf-identity-counter-v1/DATA.json"),
  DATA SHA256 `e105ebed28179fe7e78f815ec2a151b24fea172571c58b56edc727eff2fb4814`.
- [Completed primary audit](../analyses/identity-counter-live-2026-09-09/REPORT.md).
- [Post-hoc diagnostic report](../analyses/identity-counter-live-2026-09-09/POSTHOC_NUMERIC_ID_REPORT.md)
  and [machine-readable audit](../../../ARTIFACTS.md#unpublished-files "Not published: ../analyses/identity-counter-live-2026-09-09/POSTHOC_NUMERIC_ID_AUDIT.json"),
  audit SHA256 `5238d6a889c99c4e1f77e63fbb368772300b14a5fa6749ccf0eaa59100cc3dcf`.
  This proposal inspected that published audit report, not a fresh raw-response
  re-audit; implementation must bind its reused inputs independently.
