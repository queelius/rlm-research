# Operator-diverse SFT6 recovery audit

## Answer

Completing the previously unrun fixed-SFT6 arm does **not** provide evidence that this training
recipe taught acquisition, accumulation, scoped reduction, or stopping. On the conservative planned
denominator, the retained baseline scored 2/24 while fixed-SFT6 scored 1/24. More importantly, every
one of the 15 authenticated fixed-SFT6 finals was exactly `Answer: 0`; its only success was the
panel's sole zero-gold coordinate. All 23 nonzero-gold coordinates scored zero or remained NULL.
This looks like a zero-output collapse on a small, research-exposed panel, not improved operator
competence.

## Inventory and paired result

The original seal remains unchanged. Its baseline has 22/24 native finals and 2/24 strict successes
(0 count, 1 distinct, 1 weight), with one absent RESULT and one recorded native NULL. The additive
fixed-SFT6 completion has 15/24 authenticated native finals and 1/24 strict success (0 count, 0
distinct, 1 weight). Its missingness is kept in two distinct classes: two absent RESULT slots, both
weight tasks that timed out after about 181 seconds, and seven recorded native NULLs (one count,
four distinct, two weight). These are not scored as model errors.

Among the 14 pairs with authenticated finals in both arms, fixed-SFT6 has one win, zero losses, and
13 both-wrong outcomes. Ten of the 24 planned pairs are NULL in at least one arm. Planned-denominator
accuracy is therefore 2/24 baseline versus 1/24 SFT6; conditional accuracy is 2/22 versus 1/15.
Missing-data bounds are 2/24--4/24 for baseline and 1/24--10/24 for SFT6. The sole paired win is the
zero-gold item, so it is not evidence of a learned reduction.

## Actual behavior

Independent inspection of all 22 recorded fixed-SFT6 episodes found no executed `rlm(...)` call.
Thus there were zero actual child acquisitions and, necessarily, zero reductions grounded in live
returned labels. Eighteen episodes entered IPython and seven encountered at least one execution
error. Common programs searched question text for label words or indexed a nonexistent `category`
field; three mentioned `request_for` and two mentioned `strict_map`, but none executed the child call
needed to obtain labels. Some traces continued after errors, yet every authenticated stopping branch
still returned literal zero. Tool use here is therefore neither faithful dataflow nor successful
error recovery.

## Training and cost

The recovery did complete the intended optimization. The gate passed before gradients; six saved
checkpoints form the expected ancestry, and independently loaded optimizer state has 504 entries
with Adam step exactly matching checkpoint ordinal 1 through 6. The fixed final checkpoint was used,
not selected by readout. Training covered 432 example exposures, 1,944 root-turn exposures, and
137,082 current-action target-token exposures in 1,214.167 training seconds. Weighted teacher loss
at steps 5 and 6 was 0.626945 and 0.535816; these are on-support, pre-update pass measurements, not
held-out post-step evidence. No optimizer defect was found.

Recovery readout attempted 124 new physical root requests: 122 returned HTTP 200 and two HTTP 400.
It used 443,644 input tokens and 36,388 known output tokens, with output-token counts unknown for two
requests. The two absent endpoint slots consumed 32 of those requests before timeout. Capture and
baseline were not rerun. Cache use and provider billing remain unknown.

## Interpretation and next decision

This small completion neither proves that supervised operator learning is impossible nor identifies
the released-reference start as inferior. It does show that declining teacher loss and six valid
Adam updates did not make this policy enter the demonstrated child-acquisition trajectory on these
held-out prompts. Repeating the same corpus for more passes is therefore low-information. A next
training decision should first test interface reachability or use an execution-grounded warm start
on broader, independently frozen contexts; any terminal-reward follow-up should balance answer
support and score actual reduction separately from ceremonial tool use.

## Provenance and limitations

The prospective recovery method was frozen after the original infrastructure failure but before the
recovery launch or outcomes. This auditor did not author the recovery implementation, but previously
audited the calibration study and recommended the released 857 reference as a common start; that was
an operational choice, not demonstrated superiority. The comparison joins a later treatment
completion to a retained baseline, covers only eight exposed context clusters, and has substantial
treatment missingness. `RECOVERY_AUDIT.json` is the machine-readable independent recount; the
original `REPORT.md`, `AUDIT.json`, and `FINAL_MANIFEST.json` remain untouched.
