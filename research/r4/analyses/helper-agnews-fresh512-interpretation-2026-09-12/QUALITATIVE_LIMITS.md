---
schema: exploratory_changed_prediction_review_v1
date: 2026-09-12
status: posthoc_qualitative_interpretation_not_new_metric
reviewed_changed_records: 21
source_audit_sha256: 57606da1e52a5b694cad6d39dbff9febf5c66a7f6783ce3cf99e440e961f7bbb
source_text: ../../sidecars/helper-agnews-broader-data-v1/inputs/HELDOUT_PUBLIC.json
gold_source: ../../sidecars/helper-agnews-broader-data-v1/inputs/HELDOUT_GOLD.json
new_model_queries: 0
gold_labels_changed: 0
---

# What the changed answers do, and do not, suggest

MAIN read all 21 articles whose predicted category changed between the common
starting model and the eight-update RL model. This was after the numerical result
was known. It is an interpretation check, not a blind annotation study or a new
statistical test. The source articles stay in the external research store.

Several corrected examples discuss technology through commercial language:
software purchases, device launches, licensing deals, and technology services.
The starting model chose Business; the dataset calls them Sci/Tech, and RL moved
toward that category. Other corrections distinguish sports reporting from the
business transactions occurring within sports. These are understandable examples
of improved agreement with this dataset's category conventions.

The changes also include new mistakes. A wireless-capacity acquisition moved from
the dataset's Business label to Sci/Tech. Both trained models made a similar
category mistake on a luxury-airship sale. Some original dataset labels are not
obvious from their short article excerpts. We did not change those labels or
exclude examples after looking at the outputs.

Simplified examples below paraphrase the topic; they are not verbatim prompts.

| Topic | Dataset label | Before RL | After RL | Source record |
|---|---|---|---|---|
| A company adopts another company's server software. | Sci/Tech | Business | Sci/Tech | agtr1f018198c7ecf72f |
| An owner buys a larger stake in a soccer club. | Sports | Business | Sports | agtr5025d892e99fec2e |
| A wireless company acquires cellular capacity. | Business | Business | Sci/Tech | agtrbad221a228e3d7eb |
| A retailer offers a very expensive personal airship. | Business | Business | Sci/Tech | agtr2bb3141357342177 |

The conservative interpretation is that the model learned a more useful category
boundary for this panel. We have not established improved reasoning, factual
knowledge, autonomous decomposition or a new general skill. A simple change in
category preference is a plausible competing explanation, not a demonstrated
mechanism.

## What this changes in the research plan

First finish the already fixed training-seed repeat. Then test the resulting
policies on a genuinely different source partition and measure retention of the
earlier question-classification task. Do not choose new cases because they match
these attractive examples. The queued repeated-versus-varied training comparison
addresses the separate question of training breadth.

If the helper improvement repeats, test whether it actually improves the full
RLM's final answer under a fixed root policy and request format. Previous results
show that better helper answers need not repair the root's aggregation mistakes.
Keep helper-category accuracy, agreement with the supplied helper outputs, and
final problem accuracy separate. A verified gain on the helper alone is useful,
but it is not yet the architectural result the research program is seeking.
