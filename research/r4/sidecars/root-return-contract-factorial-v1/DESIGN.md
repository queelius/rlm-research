# Root weight × return-type instruction

Accepted by the main coordinator on 2026-09-09 before implementation. CPU preparation only;
the main coordinator inspects and launches the sealed job.

Question: does a minimal return-type reminder improve the original root, and does the trained
root advantage remain under that reminder? The motivating posthoc case had correct target
membership in child JSON text, but `list.extend(child.answer)` extended characters. The root
then faithfully reported its program's zero. This does not establish a general transport defect.
The main coordinator's subsequent lexical inspection of the latest native transfer first calls
found `json.loads` already present in all 13 original first-code payloads and 20/22 step8
first-code payloads; neither had the motivating literal direct-extend pattern. This suffix is
a prospective interface intervention, not a demonstrated fix for the current transfer failures.
First-call structured-tool presence, finish reason and completion length are descriptive
readouts; neither a general token-cap explanation nor full-trace semantic correctness is assumed.

Use the exact twelve root-campaign transfer tasks, two fresh hash-derived seeds per task,
six 64-record source contexts, four conditions: original root / final step8 root × unchanged /
contract. All 96 coordinates freeze before inference. These contexts and results have already
been exposed: they were root-new at the preceding transfer readout but are supported by the
fixed child's source-train SFT. This is not fresh-task, source-test, or pretraining-novel evidence.

The only prompt addition is this literal suffix, after the existing question:

> Return-type contract: The .answer field returned by rlm(...) is text, not a Python list. If it contains a JSON array, decode it with json.loads before treating it as a list.

No automatic decoding, output repair, alternate answer, oracle observation, forced recursion,
new schema, gold leakage, scoring change, or training. The baseline prompt, public definitions,
worked example, context bytes and environment remain identical. The suffix is added to the root
task prompt, not injected into child prompts; a root may choose to propagate it.

Original root: 857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6.
Final step8: 473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd.
Fixed child: c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3.
The step8 intervention is the final checkpoint explicitly requested, not new validation selection.

Reuse the qualified two-LoRA service and lifecycle V2 without edits. Two root-weight phases
of 48 episodes run in a hash-fixed order. Within each phase, paired instruction arms are
adjacent and executed serially by one worker, with first-arm order exactly balanced; eight
workers interleave pairs. Both phases use the same pair order. Root weight is confounded with
service/time/order; the design does not pretend to randomize all four arms simultaneously.
Shared-seed sampling is a coordinate match, not a promise of identical trajectories.

Native TrainClient, Qwen3 enable_thinking=True, processed logprobs, T=.5, top_p=1,
top_k=-1, min_p=0, 2048 completion cap, existing 8192 model context and all existing episode
budgets remain unchanged. Inherited nano retry delays may still occur below outer max_retries=0;
actual calls and wall time count. No new retry logic is added. Global cap 3600 seconds includes
both startups, collection, and owned-service releases; no new generation after deadline.
Reserve 90 seconds for final subprocess/runtime/service cleanup. A capped or failed attempt
is retained, not rerun; unfinished coordinates and infrastructure nulls are separate from policy
wrong/malformed outputs. The existing collector may discard partial episode traces, while native
request-local audit files can preserve calls/cost from those attempts.

Primary: exact terminal correctness, matched by task and fresh seed. Report all four cells,
contract-minus-unchanged within each root, trained-minus-original under each instruction, and
the difference of those differences. Present six context-group summaries (four matched
task/seed coordinates each), not 96 independent observations. Report planned/recorded/observable
denominators, discordant pairs, missing outcomes and runtime stops. No significance claim.

Secondary: observed TypeError/JSON parse failures; narrow static markers of `.extend(x.answer)`
and `json.loads` in root code; child calls; exact retained physical prompt/action counts;
logical usage versus cached unknown; wall time including startup/release/retry waits. Static
markers are not proof of executed data flow or hidden list contents. Missing diagnostics are null.
No extensive parser, generated-code execution, or universal full-label-map objective.

Small verification: immutable task/prompt/context equality, fresh paired and balanced plan,
wrong-root/child binding rejection, native renderer/sampler identity, root-only suffix, one
real CPU rootless fake-provider root→child→root proof per instruction arm. Fake token
probabilities are fixtures, never model measurements. Preserve source hashes and publish READY last.
