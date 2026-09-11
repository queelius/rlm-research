---
status: frozen_before_ranking
date: 2026-09-10
study: leaf-trec-test-adapter-granularity-v1
question: can native chosen-token log probabilities rank actual child-label errors?
unit: emitted record label within model x width x seed
---

# Admission and span alignment

Use only the sealed attempt-001 call `RESPONSE.json`/`RESULT.json` files and the adopted
`AUDIT.json`. Require the relayed clean owner and parent terminal pins. Load the pinned Qwen3-4B
tokenizer with the CPU-only `tokenizers` library. For every call, require that decoding the native
completion IDs while skipping special tokens exactly equals the authenticated result content and
that concatenating individually decoded token pieces does too.

Locate each JSON `"record_id":"label"` member in the exact emitted string. A label is recoverable
only when every overlapping token lies wholly inside the label string and the pieces concatenate
exactly to the parsed label. Exclude record-ID, quote, colon, comma, brace, whitespace, and terminal
special tokens. Reject rather than guess any boundary-crossing token, duplicate/missing member,
token/log-probability length mismatch, nonfinite value, or disagreement with the adopted audit.

# Frozen confidence and ranking measures

For each recovered emitted label record two descriptive scores: (1) the sum of its chosen-token log
probabilities and (2) the token-length-normalized mean. Lower (more negative) values mean lower
confidence. The sum is explicitly sequence-length-sensitive; the mean is primary. These are not
class posteriors: each probability is conditioned on the prompt and the already-generated structured
JSON prefix, including earlier IDs and labels. Only one chosen/top token was captured, so class
margins and calibration cannot be reconstructed.

Rank separately within each model x width x seed cell of 500 records. The bottom-quartile budget is
exactly 125. At a confidence tie crossing the cutoff, use fractional tie weight and report the
minimum/maximum attainable error coverage under arbitrary within-tie choices. Compare error recall
to the 25% random-selection expectation and report selected versus overall error rates. Do this for
both sum and mean scores, without choosing whichever looks better after outcomes.

# Confounds and dependence

Report results per model, width, and seed before any descriptive pooling. Report confidence and
error frequency by gold class, predicted class, and emitted-position quartile. Repeat the mean-score
ranking with the same 25% fractional budget allocated within gold class and, separately, emitted
position quartile; these are descriptive sensitivity checks for class and position composition.
Report how many contextual calls contain selected records and the per-call selected/error counts.

The 100 or 16/4 labels in a call share a generated prefix, and the same 500 source records recur over
two seeds, two widths, and two model policies. Calls/source records—not 4,000 labels as independent
samples—bound interpretation. No p-values, calibration claim, causal width claim, or claim that a
requery would correct an error is permitted. Preserve all unavailable or unalignable rows explicitly.

# Decision rule

Call the signal potentially useful only if the primary mean score covers more than the 25% random
expectation in every c32 width x seed cell and the direction survives both class- and
position-stratified sensitivity checks. Otherwise retire confidence-only selective rechecking on
this capture. A single prospective selective-versus-uniform recheck experiment may be proposed only
if this gate passes and separate supplied-plan evidence indicates child errors materially limit the
root result; it is not authorized for launch here.
