---
id: correspondence-next-mechanism-2026-09-10
status: prospective-design-only
evidence_cutoff: 2026-09-10T01:57:00Z
corrected_at: 2026-09-10T02:15:31Z
owner: question_cards
---

# Next correspondence mechanism tests

## Additive correction after MAIN review

Candidate A was arithmetically overstated: eight contexts × one seed × two mappings × two orders is
32 calls/1,536 labels, and a label-first add-on to the existing tag-first block is 16 calls, not
32. More importantly, label-first does not cleanly isolate prompt-time binding: after position zero,
each label still follows the *previous item's* emitted tag, and the sealed sparse-order96 evidence
already demonstrates previous-tag steering. Accordingly B is now ranked first and approved. The
original text below is retained as the proposal history; this correction governs the decision.

For B, only matching and visible-shift share the same 48 tag strings. Alien uses a different
one-to-one dictionary, holding cardinality and lexical form—not tag identity—fixed, with
per-position tokenizer-length matching where feasible. That is not token-semantic neutrality or FLOP
equality. Collision checks cover all visible public IDs and explicitly named local manifests at an
actual recorded scan cutoff; there is no globally-unseen claim.

## Decision

Run **A, label-first × requested referent**, first. It is the smallest direct test of whether the
622/768 versus 280/768 exact-tag result reflects correspondence already established from the input,
or whether emitting the requested tag immediately before the label steers the next tokens. Keep **B,
alien IDs**, ready as the next experiment: it distinguishes an existing-record referent from an
equally diverse but nonreferential tag. Neither is a fresh-source replication.

## A. Output order × matching/shift17 — rank 1

Question: does shifted-ID redirection survive when the label must be committed before the output tag?
Under left-to-right decoding, a later tag cannot directly prime an earlier label. Persistence of
named-record preference in label-first output therefore favors prompt-time/reference binding;
collapse toward displayed labels favors a local emitted-tag-to-next-label pathway. An interaction is
the result, not either order's marginal accuracy.

Smallest informative run: **64 calls** = eight existing MNLI48 contexts × one new paired seed/context
× matching/shift17 × tag-first/label-first. Use one seed because the eight contexts, not repeated
seeds, are the main descriptive clusters; a second seed is robustness, not replication. Freeze one
master shuffle and rotate the four cells over context. A 32-call label-first add-on reusing old
tag-first outcomes is cheaper, but ranks second-best operationally because phase/service differences
weaken the order interaction. Prefer the fresh 64-cell block if the GPU has roughly 7–9 minutes.

Hold fixed exact displayed record text/order/IDs, `requested_tag` values, common classify-displayed-
pair/copy-tag instruction, released cdbee Qwen3-4B, no tools, final-only role, temperature/top-p,
3072 cap, and per-block seed. Only ordered schema properties/required fields differ. Both orders must
use exact per-position tag constants and unconstrained three-label enums; `label,tag` must truly be
the native token order, not merely dictionary equality. Preserve wire bytes, prompt/completion IDs,
and actual decoder compilation. Exact prompt-token counts may differ and must be reported; balancing
ID token lengths does not establish equal FLOPs.

Primary metric: full-contract-gated displayed semantic accuracy on all 3,072 assignments. Primary
contrast: `[matching−shift17]label-first − [matching−shift17]tag-first`, computed in each of eight
contexts. On the frozen unequal-gold positions, report displayed/requested-named/third counts for
each order. Tag fidelity, validity, NULL bounds, finish route and native usage remain separate. No
repair/reordering. A useful decision threshold is directional persistence in at least six of eight
contexts with a materially positive named-minus-displayed margin under label-first; this promotes
input/reference binding. Near-zero interaction alone is not an equivalence claim. A large reduction
of redirection under label-first promotes emitted-token steering and motivates token-level/logit
inspection rather than another behavioral ID factorial.

Expected shape: one A100 40GB, released base, four workers, 64 calls. The completed exact-tag32 used
181 seconds collection plus startup/release; allow **900 seconds outer** conservatively (startup≤180,
collection≤600, cleanup≤90, margin30). No training/checkpoint.

Novelty limit: earlier output-order work already showed matching beats ordinal/constant when label is
first on TREC/SST, so A is not a generic field-order replication. Its new information is the
interaction with a conflicting *visible-record referent* and the named-vs-displayed diagnostic.

## B. Matching/visible-shift/alien one-to-one tags — rank 2

Question: is redirection specific to IDs that name another visible source record, or does any
position-incongruent diverse identifier degrade classification?

Smallest informative run: **48 calls** = eight existing contexts × two paired seeds × three tag arms,
tag-first exact decoder. Matching uses own ID; visible-shift uses the fixed label-blind shift17;
alien uses a frozen one-to-one set of 48 syntactically identical IDs absent from every visible record
and all reserved/source catalogs. The same alien mapping is used across the pair only after checking
no collisions. Generate IDs independently of text/gold and match the empirical tokenizer-length
multiset to the visible shifted IDs where feasible. Do not claim token-count matching equals compute
matching.

All arms share the same requested-tag field and diverse 48-tag multiset. Primary is full-contract-
gated displayed-label accuracy. The key contrast is visible-shift minus alien, with matching as an
anchor. Named-record alignment is defined only for visible-shift; for alien, report displayed/other
labels and exact tag fidelity, never invent an alien “gold.” If alien resembles matching while
visible-shift redirects, promote genuine referent competition. If alien is equally harmful, favor a
generic conditional-tag/decoder burden. If both are high, the prior result may be seed/panel fragile;
if both low, the experiment cannot distinguish reference semantics from generic incongruence.

Expected shape: one A100 40GB, four workers, **48 calls**, approximately 5–7 minutes; cap 780 seconds
outer. Main limitation: alien strings are not semantically neutral—novelty, tokenization and lexical
shape can change salience—even after length matching. A follow-up with two independently generated
alien dictionaries would test lexical robustness but is not needed initially.

## Evidence and literature boundary

Design is informed by the sealed exact-tag result (matching 622/768, shift17 280/768; unequal-gold
named/displayed/third 373/80/69 of 522), the sealed generic shifted and cue-order audits, and the
existing output-order finding above. Sources are exposed; new seeds do not make new context clusters.

The literature check was deliberately narrow and abstract-level only. JSONSchemaBench documents that
constrained decoders guarantee structure while semantic quality still needs separate evaluation
([Geng et al., 2025](https://arxiv.org/abs/2501.10868)). Dai et al. motivate entity–attribute binding
as a distinct phenomenon, but their activation-space Binding-ID analysis does not identify this
behavioral mechanism ([EMNLP 2024](https://aclanthology.org/2024.emnlp-main.967/)). Autoregressive
entity linking establishes that generated identifiers/names participate in left-to-right prediction,
not that our requested tags cause the observed redirect ([De Cao et al., 2022](https://aclanthology.org/2022.tacl-1.16/)).
No methods/results beyond abstracts and landing-page metadata were used. The three papers MAIN is
reading separately were not duplicated. These sources motivate separating schema validity,
autoregressive order and referent identity; they do not substitute for either experiment.
