---
id: rq:decomposition-stability-and-composable-returns
date: 2026-09-12
status: exploratory_mechanism_observed_adaptive_benefit_unproven
priority: high_harness_question_after_current_rl_controls
related_questions: [rq:adaptive-decomposition, rq:rl-effective-feedback, rq:sufficient-interface, rq:reduction]
evidence:
  - analyses/helper-unseen-size-transfer-2026-09-12/REPORT.json
  - analyses/helper-companion-position-local-review-2026-09-12/REPORT.json
  - analyses/helper-companion-position-local-review-2026-09-12/DIAGNOSTIC.json
---

# Can a helper interface make decomposition reliable, not merely smaller?

## What we observed

Smaller requests slightly helped question categories but harmed news categories.
At fixed group size, changing order or neighboring records changed 22 question
and 29 news predictions among 256 records. All outputs had valid keyed schemas.
Therefore, valid formatting and sensible-looking splits are insufficient.

An offline rule using two groupings and individual requests for disagreements
scored 121/128 questions in one variant, versus 117 for one grouping and 120 for
always individual requests. It spent 2.61 times the first baseline's tokens,
about 30 percent of the second baseline's tokens. Other variants were weaker;
all news variants lost to original grouping. This is exposed-data, cross-service
replay, not a deployed or learned adaptive policy. The completed three-vote
comparison scored 119 question categories and 113 news categories, versus
121 and 112 for the fixed original/A selective rule. A fresh live comparison
is now in preparation; the rule is not retuned to the new panel's outcomes.

## Relevant work changes the novelty assessment

[BatchPrompt, sections 2–3](https://arxiv.org/html/2309.00384v2) already studies
position-dependent predictions, permutation voting and confidence-based early
stopping. MAIN read these methods and the main experimental setup. Raw grouping
sensitivity, voting, and stopping on repeated agreement are not novel contributions.
Its headline token analysis excludes generated output tokens; our comparison must
continue counting both input and output, plus all extra calls.

[Cascaded Batch Prompting, August 27, 2026](https://arxiv.org/html/2608.27038v1)
separates producing answer names from mapping those answers to output symbols.
MAIN read the method, main comparisons and stated overhead: its implementation
adds an individual grounding call per item after batched reasoning. This is
related to interface design, not evidence that our keyed-output treatment or
adaptive splitting already improves performance. A separate grounding stage must
pay its full cost and compete with deterministic mapping when mapping is exact.

## Two separable research questions

**Local reliability:** Does asking the same semantic question in different groups
provide an observable warning of error, and is there a cheap action that actually
repairs those errors? Test disagreement-guided smaller requests against ordinary
permutation voting, a fixed group size, and always individual requests. Do not
train a selector until the available repair has useful headroom. On a fresh panel,
report each dataset separately rather than average away opposing effects.

**Compositional sufficiency:** Does the helper return everything the parent needs
to combine correct local answers? Consider an explicitly simplified purchase task:
find customers who bought both a bicycle and a helmet. If a customer's purchases
fall in different chunks, asking each helper only for customers who locally bought
both can fail even when every helper answers its local question correctly. Returning
each customer's purchased-product set permits exact union before the final query.

These are different problems. Better local classification cannot repair information
that the chosen interface intentionally discarded. Conversely, a sufficient schema
does not make its model-generated contents correct or complete.

## Do not repeat the existing second-family pilots

The purchase example above illustrates the principle, but it is not a new local
benchmark proposal. Reviewing the older evidence found already completed partition
and join pilots in [sufficient-interface.md](sufficient-interface.md). Ordinary
prose sometimes preserved all answer-relevant information; a deliberately lossy
local-winner baseline would therefore be misleading.

The [fresh-world file comparison](../analyses/root-fresh-join-externalization-order-live-2026-09-10/REPORT.md)
used eight generated worlds and two orders. File-only inputs yielded 12 correct
answers and 16 available finals; inline-plus-file yielded 9 correct and 10 available
finals out of 16. Among the ten fully observed pairs, file-only had no wins and two
losses. This is evidence about data access and failure paths, not a resolved
accuracy advantage or recursion benefit: there were no child calls. Some errors
followed successful loading but invented data after a NameError or used an
order-sensitive join. More repetitions without a distinct intervention are low priority.

A useful next comparison must add a real decision or mechanism: faithful recovery
from a real error, choosing a report contract, or choosing whether to delegate.
Keep ordinary reports, exact computation and direct Python-access controls.
Reuse the known generator and data-access lessons before introducing new surface
wording or deeper structures. No GPU-ready job is created by this note.

The eventual training comparison is interface by training, not a collection of
simultaneous changes. Train on shallow structures; reserve deeper and differently
connected structures for later evaluation. Plain-language narratives require
checking that the generator did not accidentally make the correct decomposition
or answers visible through template shortcuts.

## Connection to the neighboring decomposition project

The read-only research note in `../structured-decomposition-benchmark` at commit
`c7ee38127e5f37c327b77f518a21f0bab151ff33` emphasizes a useful distinction:
whether workers supply correct information, whether a combiner uses it, and
whether a proposed revision can help at all. Its existing task and results are not
imported into this program. Its lesson motivates measuring repair headroom before
training a router, while our program remains free to study recursive interfaces.

## Decision and publication boundary

Promote a direction when a fresh comparison shows useful quality/cost headroom
and a mechanism beyond ordinary voting or fixed exact computation. Replicate on
a second task family and model before a broad RLM claim. Retire simple splitting
or revision if it mostly adds calls or damages correct answers. A contribution
may concern learning sufficient intermediate information or knowing when a repair
is useful; neither is established by the current category-classification results.
