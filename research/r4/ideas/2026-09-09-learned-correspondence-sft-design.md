# Test the leaf interface before teaching correspondence

September 9, 2026; prospective decision memo, evidence cutoff 19:54 UTC. **Recommendation:
do not launch source-correspondence SFT next.** Run the smaller released-base role/tool-interface
leaf test below. This file is not a frozen design, READY, source reservation, or launch authority.

## Why the training question moved down the queue

The completed free-ID experiment changes the likely bottleneck. Its independently sealed
[aggregate audit](../../../ARTIFACTS.md#unpublished-files "Not published: ../analyses/leaf-free-id-live-2026-09-09/AUDIT.json"), SHA-256
`02885dcafcde90ef1edb140b61a65deaca620f678df696b455e5533a819c8585`, accounts for all 96
calls with exact native request/prompt checks. Exact decoding is contract-valid in 48/48 calls.
Under free decoding, matching IDs are valid in 4/8 AG News calls and score 216/512 labels on the
planned denominator; every other dataset/representation cell is valid in 0/8 calls. The 24 SST-2
free calls do not look like a clean ID-copy failure: the independent bridge audit classifies
all 24 as pursuing tool/code routes (10 parsed native tool calls, seven literal tool wrappers that
stop, and seven truncated wrappers). The frozen requests retain the inherited coding-agent system
and advertise IPython. The [final independent report](../operations/2026-09-09-allocation-5780/free-id-audit-report.md),
SHA-256 `0f946a5980255a2dc43b8dcf398fbac4681fd0f26c1cb4790438c9462082259f`,
is authoritative for that route taxonomy.

Training now would mix two interventions: learning label correspondence and learning to escape an
inappropriate agent/tool policy. Existing training evidence also makes another format-specialized
SFT low-value. The [indexed follow-up](../analyses/anchor-indexed-followups-live-2026-09-09/REPORT.md)
used 204 Adam steps and 118,198 supervised target tokens, taking 21.37 minutes of optimization on an
A100 40 GB, yet moved mixed-size B only from 373/384 to 374/384 on free indexed output. The
[training/padding controls](../analyses/grammar-training-padding-controls-2026-09-09/REPORT.md)
also show a portability cost: specialized indexed training scored 339 versus B's 444 on
anonymous/exact TREC. Output contract and runtime interface already dominate this regime. Repeating
indexed-target SFT with new IDs would not distinguish the newly observed route failure.

## Recommended pilot: role and tool availability

**Question.** Is free long-batch failure primarily induced by the inherited coding-agent role and
available Python tool, rather than by the output representation or semantic classification?

Use the unchanged released, adapter-free `Qwen3-4B-Instruct-2507` cache at revision
`cdbee75f17c01a7cc42f958dc650907174af0554` (Apache-2.0 model; complete local manifest already
pins all three tensor shards and tokenizer/config files). Cross these factors:

| Factor | Levels |
| --- | --- |
| System role | exact inherited coding-agent system; concise final-only classification system |
| Tool advertisement | exact inherited IPython tool; no tools |
| Output form | matching displayed IDs; repeated constant `p0000`; plain label array |
| Decoder | free generation; the corresponding existing exact grammar |
| Data blocks | AG News and SST-2, two disjoint 64-record contexts each |

This is `2 × 2 × 3 × 2 × 2 × 2 = 96` real calls with one predeclared sampling seed. Reuse the
existing temperature, top-p, 3,072-token output allowance, 8,192-token service context, model
alias, native template and class enums. Alternate paired request order. The final-only system should
say only that the model is a text classifier, must classify every record, return only the requested
format, and must not write code or explanations. Do not add examples, label hints, retry language,
or condition-specific rescue text. The system treatments necessarily differ in wording and token
length; they estimate deployable interface packages, not a single-token causal mechanism. Tool
presence remains a clean within-system factor once native prompt rendering is pinned.

Select four new contexts by a label-blind stable hash after a positive exposure crosswalk at the
freeze-time cutoff. Each physical record and normalized group must be absent from the explicitly
named research input/reservation catalogs in that scan, including the just-completed free-ID
contexts; this is not an all-history guarantee. Use the cached AG
News test split, revision `eb185aade064a813bc0b7f42de02595523103ca4`, which had 7,344 of 7,600
groups remaining at the last feasibility audit, and the cached SST-2 train split, revision
`8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb`, with 66,973 conflict-free normalized groups. Give
each record a unique, hash-derived displayed ID from a new namespace; freeze the same record order,
IDs, labels and user message across all interface/decoder cells. Gold labels stay host-side except
where the task's public class definitions require them.

These inputs can be new to this research history; they cannot be claimed unseen in the released
model's pretraining or post-training. AG News is cached from a card that describes research or
non-commercial source use but supplies no confirmed underlying data license. SST-2's underlying
license is likewise unconfirmed; the loader's Apache license is not a data license. Keep text in the
external research store and publish only the minimum provenance permitted by the eventual license
decision. No download is needed.

### Scoring and interpretation

The headline is **free-decoder contract-valid strict label accuracy on the full planned
denominator**, accompanied by full-contract-valid call rate. A completed malformed response scores
zero strict labels. Infrastructure-missing calls are NULL with explicit lower/upper bounds. Never
reorder labels by emitted IDs, parse prefixes as answers, execute generated code, replay tool calls,
or repair wrappers.

Store and report separately:

- native tool-call routing, literal tool wrappers, other code/prose, truncation and finish reason;
- full shape, exact tag sequence, missing/duplicate/extra/wrong IDs and field order;
- positional label correctness conditional on shape and on full contract; and
- exact-decoder accuracy and free-minus-exact gaps for each paired block.

The key contrasts are tools absent minus present within each system, classifier minus coding within
each tool condition, their interaction, and whether those changes are shared by matching,
constant, and plain forms. A broad gain across all three free forms with fewer tool/code routes
supports an interface-policy bottleneck. A matching-only gain supports an additional
correspondence-specific effect. Exact cells are positive controls for task competence; exact success
does not show that the model can freely emit IDs. With only four independent context clusters and
one sampling seed, this is an exploratory matched screen, not confirmation.

A two-seed 192-call version would measure sampling stability, but adds no context clusters and can
take up to the proposed 3,600-second cap. Prefer the 96-call screen; replicate only a
decision-changing interaction on new contexts. Before implementation, pin every rendered prompt
token vector and native request body, preserve all response IDs/usage/cost/NULLs, and set an owned
wall-clock cap from measured service throughput. No result-dependent context or seed substitution.

## Decision gates

- **Retire immediate correspondence training** if final-only/no-tools makes free output broadly
  contract-valid and closes most of the paired exact gap across representations. Standardize that
  leaf interface and test its effect on the real upstream/downstream pipeline instead.
- **Consider output-contract training** only if routing is suppressed but matching-ID free validity
  or accuracy still fails while its exact cell is strong. Require the failure to recur across both
  new contexts in a dataset; one favorable AG context is not enough.
- **Do not train correspondence yet** if exact accuracy is also weak. That is task/length capability,
  not merely ID emission; first compare shorter disjoint batches under the winning interface.
- **Treat a tools-only effect as a harness result.** It is evidence for removing irrelevant tools,
  not evidence that the model learned correspondence.

## Deferred SFT branch, if the gate opens

The practical first training question should use **full-output supervision**, not label-only masking.
Start two LoRA arms from the same cached released base: randomized matching-ID objects versus
constant-tag objects. Use exactly the same disjoint AG/SST records, grouping, order, gold labels,
optimizer and step count; retain the unchanged base as a third evaluation weight. Before freezing,
measure actual native tokenization and report target-token mass by arm rather than assuming random
IDs are single tokens or exactly mass-matched. Train at one short batch length, then cross all three weights over matching
and constant output requests, free and exact decoders, and separately frozen short and long batches.
This estimates the effect of the whole deployable training package. It cannot isolate semantic ID
association from learning to emit diverse tags.

Label-only masks are a later mechanism control: masking every prompt and ID token while supervising
only label tokens equalizes supervised mass and asks whether teacher-forced cues change label
prediction. It does **not** teach the model to produce IDs, so success under an exact grammar would
show teacher-forced cue use, not freely produced correspondence. Making it the primary pilot would
miss the observed deployment failure.

A plausible bounded SFT freeze would use 1,024 conflict-free groups per task for shared batch-16
training examples, two fixed passes, and two held-out context clusters per task/length, with midpoint
and final checkpoints retained but the final checkpoint predeclared for comparison. The historical
4B LoRA run peaked at 21.58 GB allocated and 41.40 GB reserved and took 21.37 minutes for 204 updates;
two comparable arms therefore need roughly 43 minutes of optimization plus readouts, with marginal
40 GB headroom that must reuse the proven stack rather than assume a new trainer fits. This is a
planning envelope, not a reservation or promise.

Promote SFT only if matching training beats both constant training and the unchanged base on free
matching-ID planned-denominator accuracy in both tasks, retains the effect at the held-out long
length, and does not materially regress plain/constant exact accuracy. Retire it if the advantage is
format-local, exact-only, driven by malformed-output accounting, or comparable to the historical
1/384 indexed-SFT increment. If the released model already works after the interface correction,
the fallback is no leaf SFT: spend the next GPU slice on end-to-end map consumption/length control
under the corrected interface.
