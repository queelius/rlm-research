# Independent audit: example anchoring × map visibility

## Bottom line

The run is complete and technically usable: all 32 planned endpoints have authentic native final
captures, all 89 new physical calls returned, and the owner released its service. Strict dataset
correctness is 24/32 and is exactly 6/8 in every treatment cell. Consequently every paired
correctness contrast and the descriptive difference-in-differences are zero. This does **not** show
equivalence: there are only eight paired query blocks nested in four context clusters, one seed per
block, and no discordant correctness blocks from which to estimate a treatment signal.

The strongest mechanism result comes from executed code, not answer agreement. In 25 endpoints the
root loaded `labels.json`, selected the requested users, and reduced that supplied state
programmatically. One more endpoint displayed the actual records and labels through a tool and then
performed the selection in prose; its final response violated the whole-response format. In six
endpoints—all in the example-present/file-mentioned-only cell—the root followed the API-example
skeleton, made a new child request, and replaced the supplied `labels` variable with `strict_map` of
the new child answer before reduction. Thus supplied-map agreement is not by itself evidence that
the supplied map drove the answer.

This audit began after MAIN exposed partial per-cell outcomes and call counts. It is an independent
native-artifact verification and scoped manual reduction, not an outcome-blind confirmatory claim.

## Outcomes and behavior by cell

| Optional example | Map inline | Dataset correct | Available | Strict format | Strict map-consistent | New physical calls | Supplied-map state used | New child calls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| absent | no | 6/8 | 8/8 | 7/8 | 7/8 | 33 | 8/8 | 0 |
| absent | yes | 6/8 | 8/8 | 8/8 | 8/8 | 16 | 8/8 | 0 |
| present | no | 6/8 | 8/8 | 8/8 | 8/8 | 24 | 2/8 | 6 |
| present | yes | 6/8 | 8/8 | 8/8 | 8/8 | 16 | 8/8 | 0 |

All four cells fail on the same two block-level questions: the single-user and union queries for
`new-root-train-01`. The reused map is 62/64 label-correct overall, with both errors in that context:
`q0005` is `human being` in gold but `entity` in the map, and `q0014` is `description and abstract
concept` in gold but `entity` in the map. The single-user target count is therefore 0 in the map
versus gold 1; the union target count is 1 versus gold 2. Every strict-format response follows those
map counts. This is direct contrary evidence to interpreting the 24/32 result as a root aggregation
failure: the observed dataset errors are completely explained by the upstream map on these blocks.

The lone format failure is the no-example/non-inline union query in that same context. The root
displayed the actual files, reasoned to map count 1, and ended a long prose response with
`Answer: 1`; because the contract requires the whole stripped response to be exactly `Answer: N`,
it is invalid and scores incorrect. It is not repaired or rescued.

## What was actually used

The inline condition duplicated the same map bytes in the prompt while leaving the file available.
Executed code in every inline endpoint opened `labels.json`; none parsed the inline XML-like payload.
Therefore the 8/8 inline map consistency in each example stratum cannot establish that the inline
copy was used. Inline presentation may still have changed planning or salience, but the trace cannot
identify that cognitive path.

All 16 file-mentioned-only endpoints accessed the file in some form, but access and state use differ.
The eight no-example endpoints used supplied state (seven programmatic reductions and the one manual
prose reduction). In the example-present/file-only cell, two endpoints used the supplied file while
six issued one child call each and overwrote the supplied map before counting. Those six programs
share the example's distinctive imports, `await rlm(request_for(batch))`, and `strict_map` sequence.
This is evidence of example anchoring in tool policy, even though it produced no correctness change.

The six replacement child maps were not always byte-equivalent to the supplied subsets. Four matched
exactly. The train-01 union child corrected `q0014` from `entity` to `description and abstract
concept`, but left the target-relevant `q0005` error and therefore still returned count 1. The
validation-00 single-user child changed `q0009` from `human being` to `entity`, which did not affect
the numeric-value target count. Hence equal scalar answers do not imply identical maps or identical
state use.

There is also operational counterevidence to a simple “file-only merely costs one extra read” story.
No-example/file endpoints used 33 calls versus 16 in the matched inline cell because several roots
made failed shell attempts; one tried to install `jq` inside the task executor. Example/file used 24
calls, including six children, versus 16 inline. Inline presentation is associated descriptively
with shorter trajectories here, but it simultaneously changes visibility, salience, duplication,
and prompt length.

## Native endpoint and typed-edge audit

All 32 endpoints finish with native `stop`; 31 satisfy the exact final format. For every endpoint I
matched the first physical root request token IDs to the frozen rendered prompt, located the recorded
final physical request, and reconstructed its final trace branch. The branch token sequence equals
the native prompt plus completion IDs, the native request token IDs equal the final prompt IDs, and
native message content equals the recorded root reply. All 83 root calls use the fixed RL4 root
alias; all six depth-one calls use the selected c32 child alias. Every role-audit edge is ordinary and
returned. No tool endpoint, missing row, repair, or host execution of generated code enters scoring.

The source collector reports 235.460 seconds; inclusive owner duration is 279.424 seconds under a
1,350-second outer cap. The sealed owner and rollout terminal hashes are respectively
`6b28cc1b289ba520f63601588874c373d799756461b899c3404366eeeef5d062` and
`f1777e4cc5d6582892b72ebc80ac62ec1aff475af6082f8613b7802a591cb97c`.

## Costs and provenance

The new study physically paid for 89 calls: 121,350 input tokens, 6,876 output tokens, 109,696 cached
input tokens, and 11,654 uncached input tokens; usage is known for every call. The four reused c32
map acquisitions comprise four historical calls with 4,637 input and 599 output tokens. They were
not newly paid. Summing a complete standalone pipeline separately for each of the 32 hypothetical
endpoints gives 121 calls, 158,446 input, and 11,668 output tokens; this deliberately charges the
relevant historical acquisition to every endpoint and is not amortized.

The historical authored root wrappers add eight synthetic transport requests, 6,451 prompt token
IDs and 284 completion token IDs. They are not paid policy samples; billed usage is unknown for all
eight and remains separate from native physical cost.

The reused map source is the accepted `MAPS_READY.json` closure from
`root-supplied-map-reducer-v1`. Each context's exact map source path, bytes hash, historical native
child cost, acquisition duration, and wrapper accounting are retained in `SUMMARY.json`; the source
closure and all 32 native episode hashes are sealed in `PROVENANCE.json`.

## Interpretation and next question

Within this run, removing the example or inlining the map does not change strict dataset correctness:
all four cells are 75%, all paired effects are 0, and the descriptive interaction is 0. The result
does show a sharp policy change: the example-present/file-only prompt elicits six redundant child
classifications, whereas the other three cells elicit none. Inline conditions also use fewer calls,
but the executed reductions still read the file.

This is a new matched baseline with a common clarification that explicitly names `id`, `user`, and
`text` and explains that the map is a prior child prediction. It is therefore not the old reducer
baseline, and any apparent gain in global uptake across studies is confounded by that clarification.
The experiment also cannot isolate a pure visibility effect because inline arms retain file access.

The highest-value next question is whether a factorial that independently controls the shared field/
map clarification and true map availability reproduces the policy shift across fresh contexts and
seeds. It should make the inline-only map unavailable as a file, preserve a matched no-map control,
and retain native code/state-use scoring. A second priority is whether suppressing or replacing the
first-four API example removes redundant child calls without reducing correctness. Upstream map
quality remains the accuracy bottleneck visible here, so any follow-up should report map-conditioned
and dataset correctness separately rather than treating map-consistent answers as ground truth.
