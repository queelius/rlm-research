---
schema: openai-mrcr-long-transfer-failure-mechanism-report-v1
status: COMPLETE_RAW_AUDIT
---

# Why checkpoint 32 missed six long-context endpoints

The five copy failures are exact and homogeneous: each Python observation equals the host answer
plus the linefeed added by `print`, while the model's subsequent terminal action omits exactly the
answer's final two ASCII spaces. The native completion itself ends immediately after the last
non-space answer character and then `<|im_end|>`; its decoded payload equals the preserved parsed
root reply in all five cases. Thus the experiment-scoped strip-disabled hook is working, and these
five errors were generated terminal-copy differences rather than parser stripping. Their official
marker-gated SequenceMatcher similarities range from 0.998571429 to 0.999598716, but
the frozen primary raw-exact metric correctly remains zero for them.

The sixth failure is retrieval/selection rather than delivery. The question requests the second
email about an object, but the inert generated selector searches for the second *program* about
that object. It has 0 exact user-message
matches, raises `requested ordinal is unavailable`, then the repair action reaches the 2,048-token
limit without a completed tool call or final answer. Its parsed root reply is therefore the empty
string. No child calls occurred in any of the six failures.

This sharpens the 10/16 result: checkpoint 32 produced the clean target in 15/16 contexts, then
delivered 10 exactly, lost five solely at answer-significant trailing-space copying, and selected
the wrong request type once. That is evidence of substantial procedure transfer to longer external
contexts, not a claim of broad generalization or learned decomposition. Generated programs were
read as inert strings and never executed by this analyzer.
