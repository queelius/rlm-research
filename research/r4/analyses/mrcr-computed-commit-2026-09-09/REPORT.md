# The computed-answer comparison did not reach the comparison point

The corrected six-case MRCR run made 12 actual model calls, but the model never
called `submit_text`. Consequently, there are no committed-string versus
restatement pairs. This is a useful feasibility failure, not evidence that exact
commitment helps or hurts answer accuracy.

## What happened

All six episodes used one Python call and then ordinary assistant text. All six
cells are syntactically valid Python, report successful execution, and have zero
recorded submission attempts. One final answer reached the 2,048-token cap; five
stopped normally. Total returned action tokens were 3,647 and logical input tokens
were 12,554. These are model-token counts, not measured GPU time.

Three tool observations were empty. Their code ends with an `if/else` statement
containing bare expressions, which normally does not display the expression value
under IPython's default last-expression behavior. A separate operator-authored
CPU fixture reproduced that behavior and contrasted it with a last expression
and explicit print. The other three episodes returned intact output. No transport
defect is established by these observations. The audit inspected the generated
code's syntax; it did not execute model-generated code on the host.

Two final answers reproduced a conversation's request line rather than the
requested answer. That is further reason to separate locating the right passage,
computing a candidate, exposing a value, and following the submission protocol.
Simply adding a helper does not establish that this model can use it.

## What this changes

Do not immediately multiply this same comparison across more seeds. First qualify
the submission routine with a short task-independent example or a trained
environment-use routine. Treat that as a new prompt or training intervention,
not a repair to these outcomes. Only then ask whether direct commitment preserves
correct computed content better than an extra generative step. The current six
documents are exposed development cases, not untouched long-context evaluation.

The original attempt failed before inference because its endpoint descriptor had
host/port but no URL field. That setup failure remains separate from this corrected
attempt's observed model non-submissions. Neither attempt supplies a positive
commitment result.

## Evidence

The [audit](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT.json") records per-case source hashes, syntax, submission attempts,
observation lengths, finish reasons and the operator-only display fixture.
[audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py") is read-only and uses no GPU. Primary artifacts remain under
[the endpoint-V2 attempt](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/mrcr-computed-commit-v1/outputs/attempt-endpoint-v2-001/RESULT.json").
No source, score, output or checkpoint was changed by this analysis.
