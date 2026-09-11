---
id: root-question-sensitive-metadata-transfer-v1-all-path-semantics
status: post_outcome_manual_semantic_review
date: 2026-09-10
planned_endpoints: 144
---

# Metadata-transfer all-path semantic review

This retrospective review starts after MAIN's native audit exposed aggregate
strict and availability counts. It does not alter the frozen 144 endpoints,
their native admission, scores, seeds, questions, model weights, or NULL rules.
The reviewer contributed earlier QS audits but did not author this follow-up.

Review every planned path. The qualified native audit's `available` field is
authoritative for the distinction between an observed endpoint and a true
NULL: all 17 NULLs remain unavailable, while every authenticated empty final
is an observed policy failure scored zero and remains in semantic coverage.
No generated program is reexecuted.

For each observed endpoint, manually read the sampled program sequence and
the exact parent/tool-call-linked observations on the authenticated final
branch. Record separately: successful child acquisition; usable observed
label map; requested category/operator/scope/threshold expression; whether
that correct expression actually executed successfully; whether its scalar is
grounded in the returned child labels; whether the final uses that scalar; and
strict correctness. Merely sampling a correct expression without a successful
execution is not “actually performed.” Literal ID maps may be authentic use of
returned labels but must be flagged separately. Correct zeros and other scalar
coincidences do not establish faithful execution.

The trusted `qs_problem.py` answer function may diagnose whether an observed
label error explains a faithfully computed wrong answer; it never replaces
manual path judgment, supplies a model answer, or executes sampled code.
Summaries retain planned, observed and NULL denominators; policy, primitive /
composed, zero/nonzero, context and paired strata; and both faithful-performed
and faithful-performed-and-strict counts. This is an exposed-context transfer
diagnostic, not an independent generalization claim.
