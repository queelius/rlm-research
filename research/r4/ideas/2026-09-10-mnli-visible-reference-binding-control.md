---
id: mnli-visible-reference-binding-control-v1
status: proposed_not_implemented
created_utc: 2026-09-10T10:35:02Z
evidence_cutoff_utc: 2026-09-10T10:35:02Z
question: >-
  Is the fixed-output MNLI failure caused by ambiguous slot instructions, attraction to a
  different visible record named by the slot, or inability to bind displayed text to an
  arbitrary fixed output slot?
recommended_design: five_arm_fresh40
planned_calls: 40
gpu: one_A100_40GB
outer_cap_seconds: 1200
launch_authorized: false
---

# Disambiguate visible-record attraction from fixed-slot binding

## Decision

Run one **40-call, five-arm, fresh-source interface control before training**. It is the
smallest design here that estimates instruction disambiguation and misleading-reference effects
without giving up an aligned local-identity anchor. Do not start a symbol-tuning/SFT arm unless
this control leaves a residual arbitrary-slot deficit.

This is an adaptive exploratory mechanism study. Its source groups can be new relative to named
local inventories, but they are neither pretraining-unseen nor globally unseen.

## Why this question is live

The sealed fixed-output study used unusually explicit semantic instructions: classify each
*displayed* hypothesis against its *displayed* premise; do not infer the label from position, ID,
or `requested_tag`; copy that object's `requested_tag` into `tag`. All arms used the same 48-slot
tag sequence, tag-then-label exact grammar, text/order, decoder, and paired seed. Yet displayed
semantic accuracy was 610/768 aligned, 289/768 wrong-visible, and 620/768 unrelated. On the 530
wrong-arm positions where the displayed and named records had different gold labels, 362 outputs
matched the record named by `requested_tag`, 106 the displayed record, and 62 neither. All 48
responses were native-available and contract-valid.

That rules out mere output-tag diversity on this exposed panel, but it does not uniquely identify
the mechanism. The field name still looks referential, the wrong arm supplies a real visible record
with that name, and aligned IDs offer a local correspondence cue. The current panel is
research-exposed and is not an independent replication.

Authoritative local pins:

- audit report `a433b62af3ccfcb1ae306d1fe8478959b37c5158b4df1871ccfab04499087f2d`
- audit data `1e9136d19d104e32a8fcf38f383c747324f8eaab1e180644c3f8d0710a470a1f`
- final seal `890a8c4a222a1b7eb4a6b218c24e3e56f5e2bf9bf5e3600327e25110bb5387f1`
- frozen design `1f2563a1f1f4329e0437103efee1aafb3af05bf3a06110ae334a4e02434a6935`
- prompt protocol `a3f523da86cc9b72f936441e783196e16396ee4d5c50027618ea75ce5ed87c6b`
- request bodies `1ce8749f2d9600bafd85580a3683288c1078b545100029bfc8ef0af0f57a6682`
- frozen data `e337746a0e0e057fa789c8a9b48a4aff3a81e54e193ddcd6bc0335fd79d20eec`

## One experiment: five arms on eight fresh contexts

Mechanically select eight complete 48-record MNLI contexts, two per existing genre, from the same
cached `validation_matched` revision. Before freezing, exclude every source group in the named
experiment/input/reservation inventories and record the scan interval and exclusions. Use one new
paired seed per context and rotate the five arm positions across blocks.

Keep the released Qwen3-4B base revision, final-only system role, no tools, thinking disabled,
temperature 0.5, max output 3072, context 8192, exact requested-tag grammar, displayed record order,
and label enum unchanged. Every arm gets the identical requested-tag vector and identical gold
classification problem:

1. **wrong / legacy** — exact sealed prompt semantics; each requested tag names another visible
   record (fixed label-blind shift17).
2. **wrong / explicit-slot** — identical records and tags, but the instruction explicitly defines
   `requested_tag` as an opaque output address that does not identify or refer to a record; classify
   only the premise/hypothesis in the same JSON object, then copy its address.
3. **alien / legacy** — legacy wording, but visible record IDs are fresh aliases absent from the
   requested-tag dictionary.
4. **alien / explicit-slot** — combines the explicit address definition with alien visible IDs.
5. **aligned / explicit-slot** — explicit address definition and the same object's visible ID equals
   its requested tag.

Use the same field names in every arm. Match visible-ID lexical form, cardinality, uniqueness, and
per-position tokenizer length; freeze a collision scan against public IDs and named local manifests.
Draft the explicit and legacy instruction blocks to equal tokenizer length if a natural wording
does so; otherwise freeze and report the exact difference rather than add allegedly neutral filler.
Equal token length is not equal semantic difficulty or FLOPs.

This is a chained decomposition, not an orthogonal factorial:

- explicit-slot minus legacy within wrong IDs estimates an **interface-disambiguation package**;
- alien minus wrong under each wording estimates the penalty from a **visible wrong referent**;
- aligned-explicit minus alien-explicit estimates the remaining benefit of a **local identity
  anchor** after ambiguity/conflict removal.

The last contrast is behavioral evidence about arbitrary-slot binding, not access to the model's
internal binding process. Interactions and any prompt-length difference remain named limitations.

## Metrics and interpretation

Primary: whole-contract-gated displayed-label accuracy, with 384 planned labels per arm and eight
paired context-cluster effects. Preserve completed malformed output as zero and authenticated
infrastructure absence as NULL with planned-denominator bounds. Report native availability,
tag/order fidelity, and actual prompt/completion tokens separately. For wrong arms only, report the
predeclared named-record and third-label diagnostics on unequal-gold positions; never reorder or
repair.

Precommit these decision rules (descriptive, not confirmatory):

- promote **ambiguity** if explicit-minus-legacy in the wrong arm is at least 10 percentage points,
  positive in at least 6/8 clusters, without worse availability;
- promote **visible association** if alien-minus-wrong is at least 10 points in either wording and
  positive in at least 6/8 clusters;
- promote an **arbitrary-slot binding deficit** if aligned-explicit exceeds alien-explicit by at
  least 10 points and 6/8 clusters while alien-explicit remains materially below aligned;
- revise as mixed/underpowered if effects disagree by context or wording; retire identifier-focused
  training if explicit alien performance reaches aligned performance and the wrong-ID penalty is
  removed by interface alone.

Only if explicit-alien remains low while explicit-aligned remains high should a small, separately
designed symbol-tuning/SFT comparison become decision-relevant. That training must use disjoint
training groups, randomized slot dictionaries, and held-out dictionaries/contexts; it cannot use
these evaluation groups.

Expected cost: 40 real calls, four workers, roughly 5–8 minutes of sampling plus startup/release on
one A100 40GB based on the matched 48-call predecessor; use a conservative 1200-second outer cap,
90-second request cap, complete 40-row NULL inventory, and no rerolls.

## Closely relevant primary literature (bounded read)

- Wei et al., [Symbol tuning improves in-context learning](https://aclanthology.org/2023.emnlp-main.61/),
  EMNLP 2023. Read abstract; PDF §§2–3.3 (pp. 1–3) and §6 (pp. 6–7). It directly motivates learned
  arbitrary input-label mappings and tests flipped labels, but its broad multi-task tuning is not a
  minimal explanation of this record/slot conflict; flipped-label performance also remains limited.
- Yan et al., [On Robustness of Reading Comprehension Models to Entity Renaming](https://aclanthology.org/2022.naacl-main.37/),
  NAACL 2022. Read abstract and PDF §§2–4.2 (pp. 1–5). Entity renaming can change predictions and
  increase wrong-entity errors, supporting a visible-name association hypothesis. It is an analogy,
  not an output-slot experiment.
- Li et al., [Instruction-following Evaluation through Verbalizer Manipulation](https://aclanthology.org/2024.findings-naacl.233/),
  Findings NAACL 2024. Read abstract/introduction, §3.2 (pp. 3–4), and results/conclusion (pp. 7–8).
  NLI is brittle under unnatural or flipped verbalizers and sometimes benefits from stronger
  instructions; verbalizers are class labels, however, not per-instance record addresses.
- Yoo et al., [Ground-Truth Labels Matter: A Deeper Look into Input-Label Demonstrations](https://aclanthology.org/2022.emnlp-main.155/),
  EMNLP 2022. Abstract only. It cautions that label-mapping effects depend on configuration and
  prompt/model scale; because read depth was limited, it is supporting context rather than a design
  premise.

No paper here establishes this study's mechanism. The proposed fresh chained control is what makes
the three local alternatives falsifiable.
