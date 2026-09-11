# What the official RLM implementations suggest for our next experiments

Reviewed September 9, 2026. This is a focused source comparison, not an end-to-end
reproduction or a claim that every implementation is equivalent. No active source
or running experiment was changed. [Acquisition metadata](../../../ARTIFACTS.md#unpublished-files "Not published: 2026-09-09-official-runtime-reference-acquisition.json")
records commits, trees, licenses, inspection hashes and the newly acquired source.

## Bottom line

Our core follows the same broad design as the original RLM: context lives outside
the model, Python provides a working environment, and model calls can solve parts
of the task. We should borrow good implementations and compare behavior, rather
than treat every difference as our own new method. The actual recent GPU studies
use a separately pinned Prime/verifiers/nano runtime, not the core Responses proxy.
That distinction must remain visible in reports and any eventual paper.

The existing author-repository and Lambda-RLM clones still match their respective
upstream HEADs on this date. They were reused without modifying them. A new local
snapshot of nano-rlm was cloned at `e38400695fd42c5bdc1eb133502c65c1c39da2a3`.
This was a source-only local clone, not a GitHub account fork, package installation
or replacement of the running runtime.

## Important implementation differences

| Boundary | What the inspected code does | Research consequence |
|---|---|---|
| Returning a helper answer | The [original RLM](https://github.com/alexzhang13/rlm/blob/854e688fbba9d8f8989e3da9989812e4b6dfe270/rlm/environments/local_repl.py) returns strings from child helpers. [nano-rlm](https://github.com/PrimeIntellect-ai/nano-rlm/blob/e38400695fd42c5bdc1eb133502c65c1c39da2a3/src/rlm/types.py) returns an object whose `answer` field is a string. Our core returns full Responses objects or explicit text helpers. | A typed outer object is not a validated map from source records to answers. The observed string/list misuse is a caller error, not by itself evidence of broken transport. |
| Returning a computed final answer | Original LocalREPL captures the `answer` dictionary when `ready` is set and converts its content to text. Our core already has strict `FINAL_TEXT` and `FINAL_RESPONSE`. The inspected nano loop finishes on a model response without tool calls. | Direct computed commitment is established, not a new RLM invention. The extra final-generation step is a real runtime difference worth testing where the model actually nominates a computed answer. Our prior six-document pilot produced no such nominations, so it did not estimate a benefit. |
| Preserving batch order | Original RLM preserves the order of separate batched child requests. Our `AskBatchResult` preserves response positions and explicitly identifies missing text. | Call-level ordering does not guarantee that every label inside one answer matches the intended item. The completed output-ID study tests this distinct boundary. |
| Choosing a decomposition | Original RLM lets the model write programs and call helpers. [Lambda-RLM](https://github.com/lambda-calculus-LLM/lambda-RLM/blob/3874d393483dc4299101918cf8e9af670194bd88/rlm/lambda_rlm.py) selects a task type and runs a predefined split/map/reduce composition. | Lambda-style control is a useful comparison, not evidence that the model learned its own adaptive plan. It should not replace the adaptive research question without being identified as a different intervention. |
| Resource accounting and stopping | Current nano source includes new tree-wide token/turn accounting, capped-answer salvage, role-specific prompt resolution and compaction changes relative to our pinned engine source. | A blind upgrade would change experimental semantics. Use the new snapshot as a reference or separately frozen future arm; do not silently upgrade the active campaign. Provider cache counts are accounting evidence, not measured FLOPs. |

The nano engine pinned by the qualified role overlay hashes to
`2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed`;
the current upstream engine hashes to
`3b4aa1acb21fd555daac77b81aa94484d9deba15df1ed20f135ae98a561457ac`.
The comparison inspected selected source sections and the leading engine diff;
it is not an exhaustive migration audit. The existing source and raw results stay
unchanged. Original RLM's example training configuration also should not be
assumed to fit our one-A100 environment or current trainer schema without checking.

## Three additions worth testing, without claiming their ingredients are new

### 1. Return answers with their source IDs and structural checks

A helper result could preserve its raw text and expose a strict record map, with
missing, repeated or unexpected IDs reported explicitly. It must not silently
repair labels, infer unreturned answers or mistake structural completeness for
semantic correctness. Compare raw text versus the checked representation with
the same root and child weights. Count final-answer accuracy, dropped evidence
and all additional calls. This is the most direct bridge from our strong leaf
result to a whole-RLM experiment.

### 2. Show the root which selected records remain unresolved

A small coverage record could show which caller-selected items have results,
which are missing, and where multiple returned values disagree. The root would
still decide whether to inspect, subdivide, call another helper or finish. This
could test adaptive recovery without imposing a single batch size or full-map
strategy. Start with visible versus hidden diagnostics on the same instrumented
interface. The diagnostics cannot identify a semantically wrong label without
additional evidence, and efficient target-specific plans need not classify every
record into every possible category.

### 3. Separate tool syntax from planning skill

Our first-action audit shows that part of the root-training change accompanies
better tool-request formatting. A future comparison should hold first-request
syntax usable, or use an explicit code-native action contract, and ask whether
the trained root still does better. Original RLM and our core already make
Python-code-oriented control natural; this is a discriminating control, not the
invention of code actions. It requires its own frozen decoding contract and
cannot be retrofitted into the completed training run.

These are hypotheses for targeted experiments. The potential contribution is a
measured explanation of when useful local predictions survive recursive
composition, and which interface/training changes generalize. Generic typed
wrappers, numbered answers, direct finals and model–harness alternation already
have prior work. See the [publication-positioning review](../analyses/publication-positioning-2026-09-09/REVIEW.md).

## Execution decision

Keep the existing indexed-SFT readout, root return-instruction factorial and
grammar-transfer comparison unchanged. Prepare the 128-call meaningful-tag versus
placeholder-tag control on CPU while they execute. Its [bounded brief](../operations/2026-09-09-proceed/PADDING_CONTROL_BRIEF.md)
tests a missing alternative explanation for the strongest leaf result. The
record-return and coverage pilots remain proposed, not launched. A candidate in
this document is not a result or automatic launch authority.
