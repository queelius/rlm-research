# Adaptive filter pilot v1

CPU-prepared exploratory full-policy comparison. Main alone accepts and launches.
The accepted design and CPU decision remain authoritative. No adaptive training,
new coverage reward, grammar forcing, answer repair, API retry, or outcome-based
policy/record selection is authorized.

Four new128-record TREC contexts, two declared seeds981281401/981281402, and two
plain NUM count queries (one synthetic user versus global). Historical root
adapter473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd and child
c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3 remain fixed.
The current BROAD continuation is not a policy-selection source.

The policies are operator all16, operator query-aware filter16, and a free root.
The two global fixed policies are the same executable program: eight global
executions are each referenced by two methods. There are40 distinct executions,
48 logical cells, eight context×seed blocks and four source-context clusters.
Eight blocks contain five jobs each, sequential within block and at most four
blocks concurrent. The exact rotating/reversed order is frozen in PLAN.json.
Shared outcomes/costs/failures are never counted twice as physical spend or
independent evidence. Global fixed-minus-filter is zero by construction.

## Exposure and answer skew

Exactly512 unique normalized official source groups are allocated without class
quotas or answer conditioning from the1454-group named-history remaining pool.
They remain leaf-train-supported, not all-history/pretraining-clean. Membership
and official representative checks are host-only. All optional TREC curriculum
strata are excluded. The later child-role catalogue is already within that
curriculum union; the additive catalogue check corrects its initially guessed
directory name without changing allocation. Dataset license remains unknown.

User NUM answers are2,1,2,2; global answers16,18,22,20. Always answering2 would
hit6/8 repeated-seed user episodes. This skew is retained, not balanced away.
User accuracy alone cannot establish adaptive planning. Selected IDs, plain
query handling and physical root/child work must be examined together. A cheap
correct direct-root solution remains valid; zero child calls alone proves
neither adaptation nor shortcut use. Later balanced-answer generation would
be a new design, not a revision of this pilot.

## Runtime surfaces and honest controller provenance

All arms receive only public context.txt, records.json (id/user/text), query.txt,
and the pure batch_contract.py builder/strict decoder. The free root additionally
receives the declared prompt/example, but no operator program or configuration.
Only operator arms receive operator_program.py and operator_config.json. This
corrected separation was tested inside real IPython as well as at task setup.
The free interface is new, not the unchanged historical root harness.

The owned pinned4ef3438 nano engine retains ordinary _start, child engine, broker,
native renderer/routing and cleanup. A depth0-only branch runs operator-authored
Python inside that owned IPython kernel. It uses the exact pinned tool execution,
cancellation and scope-cleanup block; the scope's spawning model request is None.
No operator code executes on the host. The child is an actual ordinary brokered
invocation. Its provider calls, IDs, token arrays and likelihoods remain native.

No sampled root node, assistant tool action or root behavior likelihood is invented.
Operator root provider calls/turns are zero; root training eligibility/likelihood
are not applicable. The inherited raw agent.trainable metadata is not rewritten:
it does not authorize treating child-only operator traces as root-training exports.
No training exporter is called by this study. An operator-computed terminal is
returned explicitly through ACP, with a separate operator transcript.

Canonical child requests omit user metadata, use original question text and
source IDs, unchanged historical definitions and free JSON-object decoding.
Strict parsing rejects duplicate/missing/unknown IDs, non-object JSON, bad labels,
nonfinite constants and trailing text; no semantic validation or retry occurs.
Returned key order is diagnostic; reduction uses ID identity. Invalid maps leave
the raw child output and policy-interface failure, with no fabricated count.
Free policy may choose other prompts, subsets, batches, direct reasoning or no
recursion. Those divergent child calls are not claimed to be paired.

Corrected owned CPU proof compares full initial child token IDs and complete
sampling objects when ordered inputs/seed coincide. It also checks actual
operator-parent/child-invocation ancestry with no spawning model request, a
metadata-filtered child request, and preservation of strict map failure. Generic
children still have ordinary tools/public-file access; requested IDs do not prove
that only those records were inspected. Operator transcripts/native-relation
files are runtime-writable diagnostics, corroborated by native request/answer
capture where possible; silent semantic inspection remains unobservable.
Operator-only program/config files also remain accessible to a generic child in
that operator runtime. Corrected qualification establishes initial native prompt
and sampling identity, not equality of every possible tool-visible filesystem
state or all subsequent behavior. This remains a whole-policy comparison.

## Endpoints, nulls and costs

Primary endpoint is the existing exact count with strict ASCII Answer: N grammar
(surrounding whitespace stripped). Correct observed terminal1; wrong/malformed
observed terminal0; empty/unanswered/incomplete terminal null. The original raw
reward is preserved separately, including its zero for an empty operator result.
No null becomes a training negative or answer fallback. A child protocol failure
is a policy-interface failure, not automatically an infrastructure exclusion.
Every planned logical cell remains in its denominator, alongside observable and
null/unstarted counts. The source collector's error-rate stop after eight attempts
is inherited; homogeneous wrong answers are not execution failures.

Preserve actual native attempts, returned/error status, IDs, depth, prompt token
arrays, logical/cached/uncached input, completion tokens and episode/service wall
time. Unknown usage stays unknown. Retain canceled attempts in native capture
even when the inherited Env discards a partial episode. Reports expose selected
operator IDs/raw maps and root sampled/tool messages; no coverage condition is
added to reward. The136 prespecified fixed child sessions are not necessarily
136 model requests, since a child may take multiple model/tool turns.

One absolute owned clock: startup≤180, cumulative collection≤2280, work2580,
owned-inclusive2700, outer2730, cleanup reserve120 seconds. Collection deadline
also intersects work_deadline−120; the inherited final60-second collection
reserve is retained. Per-episode AgentConfig timeouts are setup45, rollout300,
finalize15 and scoring15. The ordinary child tool timeout may exceed the parent
rollout cap and is subordinate to that cap/cancellation. No timer reset, duplicate
global execution, source reload into a different policy, or replacement episode.

The physical render/sampling remains native Qwen3 thinking, temperature0.5,
top_p1, top_k−1, min_p0, max_tokens2048; max_depth1 and no compaction. Fixed weight,
source, task, program, prompt/package, request and lifecycle closure travels in
SPEC/READY. Detailed CPU analysis is explicit after owned GPU release.
