# Receipt interface uptake sentinel — design only

September 9, 2026. Proposed after receipt72; no code, inputs, acceptance or launch
are prepared by this document. Main chooses whether to implement. This does not
alter receipt72, any current run, or the current broader-root priority.

## Recommendation and precise question

Prefer **96 episodes**: six existing contexts × two count questions × one fresh
task-specific seed × two fixed roots × four prompt arms. This is the smallest
proposed grid retaining every context and both task types while isolating the
procedure paragraph under fixed explicit API teaching. It is a usability and
competence sentinel before SFT, not a powered accuracy confirmation.

The completed receipt audit found unchanged21/24, indexed_raw0/24, receipt0/24.
Both new arms made zero child calls. Receipt23/24 executed source_records(),
20/24 referenced nonexistent answer_category and16/24 observed KeyError. Raw
ended empty in19/24. Therefore parser efficacy was not exercised. The old prompt
provided a full classification procedure, six-label definitions, an executable
ordinary-rlm example and explicit continuation instruction. Replacement prompts
removed these together and substituted a target-only yes/no helper example.
Failure cannot be assigned to any one of these changes retrospectively.

The proposed question is narrower: **with the public schema and helper example
taught identically, does restoring the familiar procedure increase actual helper
uptake, and does that contrast differ between original and historical step8 root?**
Once uptake occurs, receipt availability/consumption can be examined separately.

| Arm | Familiar procedure paragraph | Source-schema teaching + complete six-label helper example | Output interface |
| --- | --- | --- | --- |
| U: unchanged | Original | Original ordinary-rlm example, no new helper teaching | Original raw child answer |
| D: taught_raw_no_procedure | Absent | New common teaching | Source-ID map as raw child.answer |
| R: restored_raw | Exact original paragraph | Identical to D | Identical to D |
| V: restored_receipt | Exact original paragraph | Same common teaching; minimal receipt-consumption lines differ | child.receipt() plus unchanged raw answer |

The **only D→R text difference is inserting the exact original procedure
paragraph**. The raw code, schema, six-label definitions, continuation instruction,
context, question, model, seed and API are identical. This identifies the effect
of that paragraph under this taught API. It does NOT isolate the cause of the
earlier receipt72 failure, because D is not the old replacement prompt.

R→V estimates receipt availability plus its short consumption example, not pure
parser internals. U is the contemporaneous familiar-package reference, not a
factorial API control. All new arms are offered interfaces: no helper call is
injected, required by reward, or automatically run before the root acts.

## Fixed models, coordinates and execution shape

Original root is the existing faithful PEFT conversion:
`sidecars/single-gpu-self-sft-control-v1/inputs/step0-peft-key-conversion-v2`,
adapter857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6.
Historical root is
`sidecars/root-recovered-child-continuation-v1/outputs/attempt-001/round-08/training/checkpoint-8`,
adapter473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd.
These are the original/step8 policies already frozen in
`sidecars/root-return-contract-factorial-v1/SPEC.json`; inherit their exact adapter
configs and base identity. Do not select the current independent seed or broad16.
Child stays c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3,
the checkpoint0128 child used by receipt72. No training or checkpoint selection.

Use all six64-record public contexts and12 count tasks from
`sidecars/root-rlvr-campaign-v1/inputs/TRANSFER_PUBLIC.json`; host-only answers
and labels stay in TRANSFER_HOST_GOLD.json for unchanged final scoring. Contexts
are already repeatedly exposed, child-training-supported development data, not
new held-out confirmation. Keep exact record bytes/order, source IDs and grouping.

Proposed fresh seeds are981274301 through981274312, assigned in task-name order
(context00 human,context00 numeric,…,context05 numeric). Each task's seed is shared
across its eight root×arm conditions. These candidates must be checked against
all frozen prior seed manifests at implementation freeze; this document does not
claim a performed collision check. Freeze all96 rows before any new inference.
If a collision exists, main chooses a new complete seed block before acceptance.
No seed replacement after outcomes. There is one sample per task/root/arm, not
two independent samples within a context.

Use the unchanged native train client, renderer/prefill, depth1 and c32de child;
temperature0.5, top_p1, max_tokens2048, existing no-retry API contract and original
strict reward. Preserve actual broker and train schemas, action masks and raw
captures; no fabricated likelihood, alias mask, injected answer, fallback or
semantic validation. The helper stays the frozen ID→label map implementation.

Queue one four-arm task/root unit together. The only collector shaping should be
the previously qualified queue-group adapter3→4, with exact-source replacement
count and dispatched quadruplet coverage checked on CPU before READY. No new
scheduler. For each root use the four Williams orders U,R,V,D; R,D,U,V;
D,V,R,U; V,U,D,R, each repeated three times over the12 tasks. Each arm occupies
every position three times; each directed adjacent pair occurs three times.
Assign orders by sorted task index modulo4; shift the step8 order index by2.

Prefer three ordinary service phases using the existing single-root+fixed-child
lifecycle: original cohortA24episodes → step8 all48 → original cohortB24. CohortA
contains the human task for even context indices and numeric for odd; cohortB is
the complementary six tasks. Thus each cohort spans all six contexts and three
questions of each type; original precedes step8 for half the matched tasks and
follows for half. This avoids a new multialias service mechanism. It reduces a
one-direction root/time confound but does not eliminate period interactions;
within-root D→R remains the primary procedure comparison. A root×instruction
interaction is descriptive training-associated sensitivity, not proof of what
training causally learned. Keep phase/cohort results visible.

## Exact proposed prompt templates

Below are literal blocks. Join included blocks with exactly two newline characters
and append no extra instruction. Q is substituted from the original public task,
not rewritten. The sole task-specific code substitution is TARGET: literal
`"human being"` or `"numeric value"`, matching the public question's category.
Neither substitution includes the answer count or source labels.

Composition: U = the byte-identical original frozen unchanged prompt for that
task. D = A + T(raw) + Q. R = A + P + T(raw) + Q.
V = A + P + T(receipt) + Q. T is the common teaching below with exactly one
arm-specific consumption block. All illustrative code is prompt text only.

### A — exact common original opening

```text
The context contains general-knowledge questions, one per line. Each line has a User ID and a question, and each question's answer falls into one of 6 categories: 'numeric value', 'entity', 'location', 'description and abstract concept', 'abbreviation', 'human being'. Answer the aggregate question exactly.

The full context is stored in context.txt in your current working directory. Do not guess from the question alone. Return the requested final answer format.
```

### P — exact original procedure, the entire D→R intervention

```text
Suggested procedure: First inspect context.txt and parse each Date/User/Instance record. Read the aggregate question to decide which records and fields are relevant. If the answer needs only user IDs, count them directly in Python. If semantic labels are needed, partition the relevant records into batches, use recursive rlm calls to assign exactly one of the six labels to each record, store the assignments with record indices, then use Python to compute the requested exact aggregate. Check that every relevant record has one assignment before giving the final answer. Do not replace classification with keyword guessing.
```

### T — common API teaching and helper invocation

The text below through the first print line is identical in D,R,V. Append the
appropriate consumption code inside the same Python fence, close the fence, and
append the common continuation paragraph. In these readable examples TARGET is
already instantiated as human being; numeric-task prompts change only that string.

````text
Source-bound recursive API: source_records() returns the public records in context.txt with these fields only: id (source identifier), text (the original Date/User/Instance line), group_id and text_sha256 (provenance identifiers). The catalog does not contain answer_category, category, label, or any gold answer. Classification must be inferred from each question; do not try to read labels from catalog fields.

The following example shows a source-ID-preserving recursive classification step. rlm_records(ids, query, allowed_values) calls the child on the selected public records. child.answer is the child's raw text; the requested format is a JSON object mapping each selected source ID to its inferred label. JSON structure does not establish semantic correctness. Ordinary rlm(prompt) remains available. You may choose any relevant subset, query, batching, recovery and computation; this example does not require a particular final strategy.

Executable API example for the first four context records (a starting batch, not the final answer). You can run this in ipython:
```python
import json
from receipt_api import source_records, rlm_records
records = source_records()
ids = [record["id"] for record in records[:4]]
allowed_labels = ["human being", "location", "abbreviation", "entity",
                  "description and abstract concept", "numeric value"]
definitions = "Classify the type of answer requested, not words mentioned in the question.\nhuman being: a person, an organization or group of people, or a person's role, title or description.\nlocation: a geographic place, including a city, country, state, mountain or other place.\nabbreviation: a shortened form, or the expanded wording represented by a shortened form.\nentity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.\ndescription and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.\nnumeric value: a quantity, count, measurement, date, duration, rank or numerical code.\n"
child = await rlm_records(ids, definitions, allowed_labels)
print(child.answer)
````

Raw consumption block, identical in D and R:

```python
labels_by_id = json.loads(child.answer)
```

Receipt consumption block, only in V:

```python
receipt = child.receipt()
print(receipt)
labels_by_id = receipt["labels_by_id"]
```

Common final code, inside that same fence:

```python
if isinstance(labels_by_id, dict):
    target_label = "human being"
    print({"example_batch_ids": ids,
           "example_batch_count": sum(label == target_label
                                      for label in labels_by_id.values())})
```

Common continuation paragraph after the closed code fence:

```text
The printed count covers only the example batch, not the full context. Continue covering the remaining relevant records, retaining source IDs with inferred labels, then compute the requested aggregate. You may inspect and correct the child classifications, handle invalid outputs, change decomposition, or use ordinary rlm(prompt). A receipt's labels_by_id is null when its strict requested-ID/label map checks fail; validity never means the labels are semantically correct. Raw child.answer is always available. You decide whether and how to use these interfaces. Return only the requested final answer format when finished.
```

The common continuation mentions receipt semantics in raw arms as well so raw and
receipt teaching differs only in the small extraction/access block; it does not
make receipt() available on RawView. During implementation CPU qualification must
ensure this does not advertise an unavailable raw method: append the following
one-line interface declaration immediately before the code fence in all new arms,
using exactly the arm-specific literal shown below:

```text
D/R: This arm exposes child.answer and native metadata; child.receipt() is not available.
V: This arm also exposes child.receipt(), an optional structural validation report.
```

The D/R and V prefixes above are labels in this document, not prompt characters.
This availability declaration and the extraction/access block are the complete
R→V documentation differences. Do not add an asymmetric valid-map example,
successful fabricated child response, or gold label. The example is a valid API
invocation, not a promise that the child will return a valid or correct map.

### Q — original question, human example

```text
Question: How many records in the entire context have questions whose answers belong to the category 'human being'? Return the exact integer count in the form 'Answer: [X]', replacing [X] with the number and omitting square brackets.
```

Numeric questions use the exact same source sentence with 'numeric value'.
U's complete unchanged prompt is readable in receipt72 SPEC.tasks[].arms.unchanged
and must be copied byte-for-byte, not regenerated from this document. Its example
parses context.txt into questions, passes the same six definitions to ordinary
rlm requesting an ordered JSON label array, prints child.answer, then instructs
continuing to the aggregate. These original and replacement prompts were read
in full for this design.

## Prospective endpoints: uptake is not accuracy

Primary procedure endpoint, separately for each root: R−D in episodes with at
least one **actual native child request exactly matching a claimed helper-built
request**. Count the root's intended helper-call code separately if argument
validation prevents dispatch. Pair by the12 public task/seed coordinates. Report
gains/losses/ties and unknowns; root×procedure interaction is the difference of
these paired within-root differences. Do not pool repeated records as trials.

Report a fixed uptake ladder for each arm/root, all denominators scheduled12:

1. Executed source_records() code and observed public-catalog return.
2. Executed/intended rlm_records() invocation; distinguish source code from dispatch.
3. Native-corroborated helper request and child call; errors remain separate.
4. Returned strict requested-ID map, independently parsed and native-output matched.
5. Explicit receipt() access in V, retaining root-writable provenance caveat.
6. Extension beyond the four-record example: a corroborated helper call selecting
   any record outside q0001–q0004, or an observed alternative classification path.
7. Observable incorporation: root code reads returned mapping values to calculate
   a batch/global quantity, with tool observation where available. This is not
   proof that it causally determined the final answer or hidden reasoning.

Also count ordinary recursive calls independently: restoring P may increase
ordinary rlm uptake while the helper remains unused. That is successful familiar
decomposition with missing helper adoption, not helper competence. Report unique
requested subsets per query/vocabulary; do not impose a full64×six-label vector
as a reward or collapse distinct semantic queries into one coverage denominator.

Structural receipt validity has no semantic-gold component. No helper call means
not-applicable map coverage, not invalid maps. Preserve raw results and every
helper/transport/policy error, no replacement episodes. Root-writable logs are
claims; corroborate selected source bytes/request text and response against actual
child native capture. Access alone is not consumption or benefit.

Keep original strict final numeric success as secondary, with valid-wrong,
malformed, empty terminal, infrastructure-null and unrun/censored counts separate.
Report R−D, V−R and new-package−U success contrasts, but do not infer a receipt
effect among outcome-selected helper users; post-hoc conditional comparisons are
selection-biased. Report all physical root/child attempts, actual input/action
tokens, missing cache measurements, length finishes and wall/owned-service time.

## Decision rules before spending on helper SFT

These are practical descriptive thresholds, not significance cutoffs. “High”
uptake means at least9/12 native-corroborated helper-using episodes for a root;
“low” means at most2/12. Inspect all six contexts, not just the pooled threshold.
At least6/12 extending beyond the example is a separate minimum for calling the
bridge usable beyond literal imitation. The middle region is inconclusive.

- D low, R high: evidence that the familiar paragraph enables helper uptake under
  fixed teaching. Prefer prompt restoration over SFT. It does not diagnose the
  old run's entire failure or prove the paragraph alone suffices without teaching.
- D and R high: explicit schema/example teaching suffices without the paragraph.
  Do not train simply to recover an already demonstrated interface competence.
- Ordinary calls return in R but helper stays low: the paragraph restores the old
  strategy; API adoption remains deficient. Consider a narrowly supervised bridge
  only after CPU fake-broker execution of these exact snippets succeeds and the
  helper offers a decision-relevant advantage worth teaching.
- Original high, step8 low under identical R teaching: a small train-only bridge
  preserving the old strategy is more justified than broad helper SFT. This is a
  training-associated interaction with residual period caveat, not proof of harm
  from a particular update. Preserve an unchanged-policy retention evaluation.
- Both roots low in D/R/V despite correct snippets: retire this optional API
  packaging for the remaining allocation, or make one explicitly authorized
  interface-teaching intervention. Do not leap to SFT as the explanation or force
  helper execution under a supposedly free-policy claim.
- R/V both high, V accesses receipts and extends beyond the example, but structural
  checks are almost always valid and exact success/cost does not improve: retire
  the receipt-benefit hypothesis for this easy setting. A later test would need a
  naturally error-prone decision-relevant setting, not manufactured reward gains.
- V has useful consumed failure signals and better exact success without material
  extra cost: prioritize new-context replication; only then consider a minimal
  SFT bridge to an already useful behavior. Success among selected users alone is
  insufficient. Semantically wrong valid labels can survive perfect validation.

No decision to train, retire or replicate is executed automatically by this
sentinel. Main reads all endpoints and determines the next resource allocation.

## Cost, qualification and stop conditions

Expected occupancy is roughly12–20min, not the8min receipt72 envelope: successful
uptake could increase child calls toward the unchanged arm's~14physical calls per
episode, and original-root tails have previously reached~364s.96episodes may
produce~1,000–1,500 physical calls, depending on free decomposition. This is a
planning estimate, not an equal-compute promise; prompt lengths must be measured
and frozen without padding or cache assumptions.

Propose cumulative collection cap1800s across the three phases, with450/900/450s
phase limits, shared work deadline2280s including service startup and CPU checks,
owned-job cap2400s including normal120s cleanup reserve, outer cap2430s. No timer
resets when changing root phase. If a phase cap is reached, retain unanswered and
unrun coordinates; never silently substitute later samples. Keep the allocation's
earlier hard deadline authoritative. Main can choose a smaller cap before freeze,
with explicit risk of incomplete paired cells. No per-episode scientific budget
or automatic retry expansion is proposed.

Before any READY, narrowly qualify the two exact code snippets in the existing
owned CPU fake-broker runtime: valid/incomplete/duplicate/unknown-ID fixtures,
normal child response and honest public catalog with no category labels, raw
preservation, receipt only on V, gold absent from setup. Confirm D/R byte difference
is exactly P, source grouping dispatches complete quadruplets, all96 inputs and
12 seed bindings are frozen, roles/weights unchanged, and cleanup remains owned.
Reuse pinned native capture and the accepted absence-observer lifecycle wrapper;
no broad refactor, new scheduler, semantic validation or API fallback.

## Cheaper alternative:72 episodes

Drop D only: the same six contexts×two counts×one seed×two roots×U/R/V. Keep all
other prompts and endpoints, balance six three-arm orders twice per root, and
use the same root-order cohort strategy. This reduces samples and likely cost by
about25%, while still showing whether a complete bridge restores uptake and
whether receipt is accessed. It cannot isolate the procedure paragraph from the
schema/example teaching. Choose72 only if the immediate decision is strictly
“does this prompt package suffice before SFT?” rather than “which part of the
teaching is needed?”144episodes is not necessary for either sentinel; adding a
second seed can follow demonstrated useful uptake rather than precede it.

## Source-grounded evidence

Receipt audit: analyses/receipt-ablation-live-2026-09-09/REPORT.md
SHA3e44c08abec9abaf2b7dfd40299b8f9e60906ccf5192ad26f900c5fdd02b29a6;
AUDIT.json1ceb29a097b1fea748a8f34df6c29f4ab5613fcfca884b38cba17bca92314356;
SUPPLEMENT.jsond6423c66631c86e79ae8300a52ba7582789c5be8fe0c60cb2c1687ed9f2d9432.
Exact old/replacement prompts and scientific contracts:
sidecars/root-receipt-ablation-v1/SPEC.json
SHA90000411c23cc92ad1ed21906cd30a5687bfa315e509b19eecc9e3792532b198;
experiment.py1803aa59cfaf94edf7ac5db865cce4c721eb2302b31ab186c5b88b0fc4488690;
receipt_api.py4ffaccc9ad15ee088ab1f6d50545a8d9bf269cf2481febaf5bf5d42e333706a6.
Historical model choices: sidecars/root-return-contract-factorial-v1/SPEC.json.
Cost/tail context: analyses/root-continuation-live-2026-09-09/REPORT.md.

The brainstorming skill kept this work at design/contrast selection and explicit
approval boundary. Only this idea document was added; no implementation follows
without main's separate decision.
