# Matching record IDs have a local, position-dependent benefit

![Raw label accuracy for the same records](../../../../ARTIFACTS.md#unpublished-files "Not published: same-record-reminders-v2.png")

The blue line uses the correct record ID as an output reminder; the brown line
uses a constant placeholder. A reminder appears every four labels. Moving that
reminder lets us compare **the same records** at the reminder and one, two or
three labels afterward. This addresses the possibility that reminder positions
merely happened to contain easier records.

The matching-ID condition is much more accurate near the reminder. Its advantage
then shrinks, while the constant-placeholder condition is relatively flat. The
pattern appears in all three classification tasks. It is a behavioral result,
not a measurement of internal attention or proof of a particular memory mechanism.

| Task | At a matching ID | Three labels later | Constant placeholder, at / three later |
|---|---:|---:|---:|
| Question types |93.2%|38.1%|32.0% /32.8%|
| Movie-review sentiment |94.5%|69.1%|54.5% /56.8%|
| News topics |81.8%|33.8%|29.7% /32.6%|

These percentages are **correct individual labels**, not whole-RLM answers. None
of the192 complete64-label replies got every label right, although all had valid
structure. This particular experiment uses one fixed research-trained helper;
the separate released-model experiment is not pooled into the plot.

## What the figure averages

For each task, all four source-context batches are included, with two generation
seeds per batch and eight phase/ID conditions per seed:192 model calls total.
The primary comparison excludes the first three records, leaving the same61
records at every distance in every batch. Two seeds are averaged within each
context, then the four contexts receive equal weight. Repeated labels and calls
are not thousands of independent tasks. The lines connect four observed means;
they are not a fitted decay model or a population confidence interval.

The output structure supplies the IDs; this is not evidence that the model learned
to retrieve IDs freely. Moving reminders also changes preceding generated text
and which positions use objects rather than strings. Those differences are part
of the intervention and remain plausible explanations. The full audit reports
context-level effects, the matching-minus-constant primary comparison, provenance,
costs, and the separately preserved zero-call launch failure.

[Full independent audit](../reminder-phase-live-2026-09-09/REPORT.md) ·
[Vector figure](../../../../ARTIFACTS.md#unpublished-files "Not published: same-record-reminders-v2.svg") ·
[Numeric data and source hash](../../../../ARTIFACTS.md#unpublished-files "Not published: DATA_V2.json")

## Reproducibility and visual check

The plot authenticates the sealed METRICS file with SHA256
69a9dd008323844589c5ada24f44b1b33a6c23f0927cd2802212f7dd580ac32f,
then independently recomputes raw-arm means from all24 seed blocks. Two focused
reducer tests pass, covering denominator/equal-context arithmetic and missing,
duplicate, wrong-seed, invalid and out-of-range blocks.

An initial reducer assumed context numbers restarted within each task; the actual
frozen catalog numbers them0–11 across tasks. Its explicit mismatch stopped before
any figure was created. The corrected reducer binds the three exact four-context
ranges. Visual inspection then found first-point annotations crowding the100%
tick labels. The v2 rendering moves those annotations only; DATA.json and DATA_V2
remain identical. Original figures are retained but superseded by the v2 links.
MAIN inspected both PNGs; the v2 annotation/tick overlap is resolved.

This is a new visualization namespace; no sealed scientific source, outcome,
earlier report, checkpoint or active service was edited.
