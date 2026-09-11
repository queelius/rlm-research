# Adaptive user filtering: executable 40-execution pilot

Design-only proposal, September9,2026. No dataset, implementation, READY, acceptance
or launch is created. This refines the adaptive-family/feasibility notes and the
correspondence-to-query-sensitive-planning memo. Checkpoint8 auditing has priority
over this preparation. The design does not use BROAD16 outcomes to choose weights.

## Recommendation and what it can identify

Use four new128-record TREC contexts, user-specific NUM versus global NUM queries,
two fresh rollout seeds, and three complete policies: operator-authored all16,
operator-authored question-aware-filter16, and a free historical step8 root.
Collect40 distinct executions representing48 logical cells. The eight global
all16/filter16 cells are identical complete programs and share one execution each,
prospectively. Do not duplicate them merely to fill a table.

This tests whether a real child-assisted metadata filter offers an accuracy/cost
opportunity and whether the free policy exploits it. It is not isolated routing
causality: controller authorship, root inference, wording of freely chosen child
requests, batching and reduction can differ. A correct global histogram does not
prove correct record correspondence; a user-conditioned count makes some such
misattachments consequential. Neither question logically requires a six-class
coverage certificate as a reward condition.

## Fixed models and runtime

The root is the prespecified historical eight-update checkpoint, not a newly
selected BROAD16 intermediate:

- Path: `sidecars/root-recovered-child-continuation-v1/outputs/attempt-001/round-08/training/checkpoint-8`.
- Adapter: `473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd`.
- Adapter config: `96bdfd4c119ebca1a8ded6f766a5fa86441fd17df56c6e69314811eac722a896`.
- Child: `sidecars/trec-leaf-sft-v1/outputs/attempt-001/checkpoint-0128`, adapter
  `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`, config
  `ec773bc3b9de58af98a7c4dce9a40af795a4d05cd47284dbbfb27eac99b74174`.

Reuse the current pinned native TrainClient/Qwen3 renderer with thinking enabled,
actual request-local depth routing, and owned rootless image
`sha256:53a70288e91a75c9bc8cbc9a75da4c3d156227266fd8c6c997deb8ef7f921552`.
The nano runtime is **4ef3438d55fdd39b18d34035833c73e13b006733**, not the separately
cached newer e384 checkout. No host-generated model code executes: all root/child
Python, including operator controller code, runs inside the newly owned runtime.
No environment or shared checkout mutation is proposed.

Sampling is the common frozen native contract: temperature0.5, top_p1, top_k−1,
min_p0, max_tokens2048, same coordinate seed on all model calls in a tree,
max_depth1, no compaction, no service/API/episode retries. Keep ordinary child
tools and system prompt unchanged; do not add the separately proposed child-role
prompt or force a decoding grammar. The generic child can itself use Python or
read accessible public files; a selected8-record request does not guarantee that
only eight records were inspected internally. Record actual tool/model behavior.

## Data allocation, metadata and exposure

Use the named-history remaining pool from `2026-09-09-adaptive-question-feasibility.json`:
1,454 normalized leaf-training groups, set digest
`db4418a688e759bf159b2a24922caa32c7115c358b007d74c10ba7e87003dff2`.
The source split is `36e7d2e1ad83210f6420a0312ec46e8a8c70d764e9df0e6d631c67f6fd16c764`,
split-file SHA `3f5f648488d512d2052b9f3d57c02e030af8e939ca363998c07a556a47d7f457`.

Freeze namespace `adaptive-filter-pilot-v1` and select512 groups by ascending
SHA256 of compact JSON `[namespace,"source",group_id]`; divide into four128-row
blocks in that order. Use the frozen official source representative for each group.
No class quota, label balancing, successful-child screening, answer-based user
selection or resampling. This is a new allocation, not the already exposed
feasibility-preview documents. The resulting IDs/bytes/hashes are an implementation
deliverable; this design does not pretend to have generated them.

For context index0–3, assign16 synthetic users with exactly eight rows per user.
Hash-sort positions using `[namespace,"user-position",context_index,position]` and
assign the fixed multiset `u00` eight times, then `u01` eight times, etc., to those
positions. Assign public IDs q0001…q0128 by displayed position. Query user is
`u00`, `u01`, `u02`, `u03` for contexts0,1,2,3 respectively. These choices never
consult semantic labels. Omit dates from this two-family pilot; they add no useful
factor here. Public records contain only `id`, `user`, and original `text`.
`records.json` and a readable `context.txt` encode exactly those same records;
there is no `answer_category`, label, target witness, oracle subset or hidden hint.

Named exclusions must be reconstructed from the feasibility inventory before
preparation closes: legacy OOLONG windows6/8; root-only PUBLIC; both campaign
TRANSFER_PUBLIC files; leaf-composition DATA; and **all** root-curriculum GROUPS,
including unused optional strata. Confirm the later return-contract/receipt/
uptake/child-role catalogues introduce no additional named root context beyond
that union; if a newly prepared catalogue does add groups, subtract them by the
same rule and report the new pool digest before allocation, without outcome
screening. Contexts are mutually group-disjoint and disjoint from those enumerated
root studies, not from every possible historical/paraphrase/pretraining exposure.
They deliberately remain leaf-train-supported. Excluding the entire upstream
OOLONG pool would leave only278 groups and cannot support these four documents.

Host-only gold is computed after public allocation: NUM count among the queried
user's eight rows and among all128 rows. Retain the full answer histogram, zeros,
class histogram, requested-user subset size and per-context constant-answer
baselines. Preview skew is already known; do not change this allocation if the
new user answers are mostly0 or1. Label-balanced sampling would change the
estimand and is not this proposal. Data license remains unspecified/unknown;
loader-code licenses do not imply dataset rights.

## Exact public query and free-root prompt proposal

Use these complete query strings, differing only in their intended scope:

> How many records from user u03 ask for a numeric value?

> How many records in the entire file ask for a numeric value?

Proposed common free-root task text (u03 is replaced by the frozen context user):

> The public file records.json contains a JSON list of128 records. Every record
> has an id, a synthetic user, and text containing the original question. context.txt
> is a readable copy of the same records. Users are synthetic metadata, not semantic
> labels. Count records, not distinct users. “Numeric value” means the category
> defined below. Classify the type of answer requested, not words mentioned in the
> question.
>
> human being: a person, an organization or group of people, or a person's role,
> title or description.
> location: a geographic place, including a city, country, state, mountain or other place.
> abbreviation: a shortened form, or the expanded wording represented by a shortened form.
> entity: a nonhuman, nongeographic thing or name, including objects, organisms,
> works, events, substances, methods or synonymous terms.
> description and abstract concept: a definition, explanation, reason or manner
> of doing something, rather than a particular name or number.
> numeric value: a quantity, count, measurement, date, duration, rank or numerical code.
>
> You can use Python and ordinary `await rlm(prompt)` to ask a child for help.
> `batch_contract.py` contains the documented pure request builder and strict raw
> JSON decoder shown below; neither calls a model or chooses records for you.
> You may use them, write your own request, inspect the original text yourself,
> choose subsets and batch sizes, or use another valid computation. No helper call
> or complete label map is required. Model labels may be wrong even when JSON is
> valid. Return only `Answer: N`, where N is a nonnegative decimal integer.
>
> Question: How many records from user u03 ask for a numeric value?

Embed the *unchanged six-class definition string* from the historical executable
root example into the final prompt/package and canonical builder. Its actual
`DEFINITIONS` value is in `sidecars/trec-leaf-contract-probe-v1/driver.py` at32:
string SHA `b4c783af63b6c94b79750471c9b129c686de6cd1661c3fac95b695012cc34860`,
source SHA `a82baf0d9be7f5cbc756ced908c405f6aba4497b46a4ca56e15c8900798c8bce`.
The quotation above wraps long lines for readability; construction uses those
exact string bytes, not Markdown line wrapping or reworded class boundaries.

Optional API usage example, identical in all policy packages, with no initial
model-generated or forced helper call:

```python
import json
from rlm.api import run as rlm
from batch_contract import request_for, strict_map
records = json.load(open("records.json"))
batch = records[:4]
child = await rlm(request_for(batch))
labels = strict_map(child.answer, [row["id"] for row in batch])
print(labels)
```

The example documents an ordinary API, not a new receipt or automatic classifier.
The module is a small public serialization/parser library available equally to
all arms. `strict_map` performs no request, repair, semantic validation or selection.
Free-root non-use is allowed and is not a task failure. The task question remains
plain text; do not provide a hidden machine-readable planner target to the root.

## Deterministic policies and exact child contract

The operator programs parse only the two frozen plain-query forms. Both read the
same public records and classify with the same `request_for(batch)` function.
The all16 program classifies all128 in displayed-order blocks of16, then reduces
over the whole map or the requested user's entries as appropriate. Filter16 first
filters the public user field only for a user query, retaining displayed order;
it classifies the resulting eight records in one batch. On a global query it is
the same all16 program. Neither baseline reads labels or uses oracle semantic
inspection. Batch maximum16 does not pad the eight-row filtered request.

Readable controller sketch for the future owned-runtime implementation:

```python
records = read_public_records()
query = read_plain_query()
requested_user = parse_exact_user_query_or_global(query)
selected = records
if controller == "filter16" and requested_user is not None:
    selected = [r for r in records if r["user"] == requested_user]
labels = {}
for batch in chunks(selected, 16):
    child = await rlm(request_for(batch))
    labels.update(strict_map(child.answer, [r["id"] for r in batch]))
relevant = records if requested_user is None else [
    r for r in records if r["user"] == requested_user]
count = sum(labels[r["id"]] == "numeric value" for r in relevant)
write_operator_result(answer=f"Answer: {count}")
```

This sketch is not executed or promoted as qualified code. `strict_map` rejects
top-level non-object JSON, duplicate keys, missing/unknown IDs, non-string or
out-of-vocabulary labels, nonfinite JSON constants and trailing text. It never
repairs an answer or retries. A model-authored structural failure stops the fixed
program with a recorded `child_protocol_failure`, raw answer preserved, and no
invented final count. A correctly shaped but semantically wrong map is reduced
as returned and scored against host gold. Returned order is diagnostic; ID keys
determine reduction. Programmatic selection uses metadata, not model labels.

Canonical request, serialized deterministically with compact UTF-8 JSON:

> Classify the type of answer requested by each question using these TREC definitions:
> [exact pinned historical definition string]
> Return only one JSON object mapping every supplied id exactly once to one label.
> No missing or extra ids. Allowed labels: [the six full historical label strings].
> Records: [{"id":"q0001","text":"original question bytes"}, ...]

User metadata and the parent user/global query are not included in the canonical
classification request: they are irrelevant to question type. For the same ordered
record IDs, builder version and coordinate seed, child input strings and sampler
must be identical. All arms retain the same actual child system prompt, tools,
native renderer, base/adapter and runtime configuration. Preserve any environmental
prompt text, session paths or context metadata that the native system renders;
qualification must compare physical token IDs, not just assert text equality.
The pinned `_load_system_prompt` uses cwd/skills/tool/depth settings rather than
the random session directory as a prompt argument; common `/app`, fixed skills
and depth1 should therefore permit identical initial child tokens. This remains
a CPU-qualification obligation, not a measured fact here. If a volatile path or
other difference is found, retain both physical payloads and report that the
exact-token pairing contract is unmet before READY; no silent normalization or
prompt patch is authorized. Divergent free-root requests are
full-policy trajectories, not paired child calls. Identical seeds also do not
guarantee deterministic repeated GPU outputs.

## Exact minimal source seam: operator root, real child

Three approaches were considered:

1. **Preferred: owned depth0-only engine adapter.** Keep Prime SingleAgentEnv,
   RLMHarness/ACP, runtime lifecycle, nano broker, child engine and native capture.
   At the start of the pinned `_run_loop`, dispatch the frozen operator program
   only when depth0 and the immutable episode policy is scripted; otherwise run
   the original function unchanged. No fake provider response or sampled root node.
2. **Custom Prime harness launching a child-only operator runtime.** Also honest,
   but duplicates more ACP/provider/configuration glue and complicates exact
   child-environment matching. Use only if the narrow engine seam fails CPU proof.
3. **Ask the model to follow the fixed plan, or replay fake model tool completions.**
   Not suitable: the first is not deterministic, and the second invents model
   behavior/likelihood. Neither estimates the proposed executable baseline.

The actual pinned seams inspected are:

- `leaf-contract.7HPUr5/nano__engine.py`: SHA
  `2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed`;
  `_start` line296 initializes the normal supervisor, IPython kernel and messages;
  `_run_loop` line382 is the depth0-only dispatch seam; its tool section around480
  opens/closes scopes and safely settles tool cancellation. Reuse that behavior
  rather than calling a blocking kernel from the event loop. `_call_model` remains
  unchanged for every real model call apart from the already qualified role headers.
- `recursive-example.6xBrmx/src__rlm__supervisor.py`: SHA
  `1b9a1b303b7c2a389d8981d0c7ea9d3e5603b49f8a420f354220c6a28c9cc78e`;
  `open_scope(invocation_id, request_id=None)` at234 explicitly accepts a scope
  without a spawning model request. `_run_child` at320 creates the ordinary depth1
  engine using inherited runtime configuration; it is not replaced.
- `recursive-example.6xBrmx/src__rlm__semantic.py`: SHA
  `7da04fcdabfd9d1086aa98f7ad7ac09ddeab3b6076222dc0a5ca867855ab60d1`.
  Register the operator parent with no spawning model-request edge. Record real
  child session/request IDs; do not manufacture a nonexistent parent sampled call.
- Prime `deps/verifiers/verifiers/v1/acp/__init__.py`: SHA
  `c143d95580458c9b8e9c822860e34116e034e00d4325ffdd3b2298dd0c0adfb4`;
  line289 records the ACP reply as `trace.root_reply`, separately from native
  intercepted model calls. Therefore an operator-computed terminal can be explicit
  without pretending that a model sampled it.
- Prime `.../harnesses/rlm/harness.py`: SHA
  `7256f1efe1d0b44c8488e62edc93c41fa2da1fae95620bc6de4dea2e7d517bfc`;
  setup/prepare_acp/_runtime_metadata retain the qualified owned-container setup,
  interception and inherited child settings.
- `sidecars/root-only-credit-v1/native_routing.py`: SHA
  `5ea35866be87662372ca1b312ddabbbab9ce009915fbfaa31353455ec702e841`;
  `installed_hooks` preserves exact native request/result capture and real depth
  routing. Qualified owned role overlay source SHA
  `8575081694a6ceea8d5f4058d4f625eb81d34f617a680f94bc06968e3a3ca78f`.

The operator branch runs the frozen program using the initialized real IPython
tool and a supervisor scope with `request_id=None`, closes the scope and returns
its computed `RLMResult` through ordinary ACP. Record `controller_kind=operator`,
program hash, inputs, selected IDs, raw child outputs and final result separately
from assistant messages. Root model calls/tokens are0; root behavior likelihood
and root-action training eligibility are **not applicable**, not synthetic zeros.
Each child completion retains its real native IDs/logprobs/usage. Whole-root
training exporters that require sampled root actions are inappropriate for these
scripted baselines; use a child-call audit plus operator transcript, not a repaired
root training graph. Task setup copies public files only; gold stays host-side.

This is source-grounded feasibility, not completed qualification. CPU preparation
must prove the actual pinned ACP/runtime accepts child-only sampled traces with
an operator terminal, preserves strict scoring, returns zero root provider calls,
and retains raw child failures without fake semantic parent edges. The currently
available newer e384 checkout was useful orientation but differs from4ef3438 and
must not silently replace it. Any additional runtime source needed for the adapter
must be resolved from the frozen4ef installation/provenance before READY.

## Forty physical executions,48 logical cells

Declare rollout seeds981281401 and981281402 prospectively; repeat them across
matched methods/query families for a context. Confirm no exact seed collision in
the named source manifests at preparation. A collision is a pre-inference source
decision for the parent, not authority to pick another convenient seed. The two
seeds are repetitions, not two new contexts.

| Family | Logical cells | Distinct executions | Fixed child-session requests |
| --- | --- | --- | --- |
| User NUM |4contexts×2seeds×3methods=24|24|64 all16 +8 filter16|
| Global NUM |4contexts×2seeds×3methods=24|16:8 shared baseline +8 free|64 shared all16|
| Total |48|40|136, plus free-root recursive dispatches|

The136 count is **recursive child-session dispatches**, not necessarily136 model
requests: a generic child can make multiple model/tool turns. Keep the distinction
in the compute proposal and audit. No label cache is shared across distinct
executions. In particular, all16 user/global executions remain distinct even when
their leaf requests coincide, because their terminal aggregation differs.

Freeze a physical execution table and a separate logical-reference table. Each
shared global execution has two logical method references to the *same* outcome,
cost and failure. Count its physical tokens/time once in campaign spend; report
that same cost under each method's hypothetical global policy cost, without summing
those tables as actual spend. Global all16−filter16 is0 by construction, not an
independent observed treatment effect. Bootstrap or descriptive paired summaries
must resample the four context blocks with both seeds and preserve the shared ID.
Do not use48 as an independent sample size or treat two shared failures as two events.

Use eight context×seed blocks containing five physical jobs (user all/filter/free,
global shared/free). For block j=2×context_index+seed_index, define base order
`[user_all,user_filter,user_free,global_shared,global_free]`: j0–4 use left rotations
by j; j5–7 use left rotations of the reversed base order by j−5. Each job type
occupies every position once or twice. Dispatch four blocks concurrently at
most, sequential within a block; fixed controller batches are sequential. Publish
the exact40-job order and48-to40 mapping. Shared global jobs are executed once in
their slot; downstream comparison references never trigger another run.

## Outcomes, failure accounting and tentative cap

Primary display: exact successes per eight planned cells for each family/method,
observed strict scores, complete paired gains/losses, and physical cost by four
context clusters. A correct observed `Answer: N` scores1; an observed wrong or
malformed final answer scores0. Unanswered tasks have strict score null. Distinguish
completed child-protocol failure, model refusal/empty result, infrastructure failure,
timeout/cancellation and unstarted-at-cap, retaining raw evidence for each. A fixed
controller's invalid child map is a policy-interface failure, not automatically
infrastructure; it does not license a guessed count or host repair. Planned success
fractions are coverage-sensitive lower bounds when any score is null, and must be
shown with the failure breakdown and answered-only denominator, never alone.

Keep root/child calls, all actual model-request attempts, logical/cached/uncached
prompt tokens, output tokens, tool times, elapsed episode wall, observed source IDs
and actual returned-map alignment. Count repeated record requests and count errors
before/after metadata reduction as diagnostics when reconstruction is possible.
Coverage and cancellation diagnostics do not alter strict correctness reward.
Free-root direct semantic work is not visible in a child-call count; fewer child
calls do not alone mean lower total model work. Root-written logs are corroborated
against native capture or explicitly marked untrusted/unobservable.

Tentative inclusive envelope2700s, comprising work2580s plus120s owned cleanup;
tentative outer2730s. Within work, propose service readiness≤180s, cumulative
collection≤2280s, and final artifact bookkeeping≤120s, all bounded by the one
absolute deadline, never additive timer resets. Per execution propose setup45s,
rollout300s and finalize/scoring15s each, still subordinate to the global cap;
all arms use the same settings. Exact inherited timeout field semantics and cleanup
behavior need CPU qualification before acceptance. No expectation that every worst-
case timeout can fit. Keep every partial, stop starting jobs at the deadline, and
do not replace failed episodes. This is a45-minute exploratory allocation estimate,
not measured guaranteed throughput. Reprice after bounded CPU qualification and
existing child-runtime timings, not after selectively running favorable pilot cells.

## Readiness gate and next decision

CPU-only implementation can proceed only after the parent accepts this design:
prepare public512-row membership/provenance and host-gold separation; freeze the
40/48 dependency table and exact prompts/programs; qualify operator→real broker→
fake-child→operator terminal in the owned runtime, plus an unchanged free root
fixture. Require zero fake root model completions in scripted arms, real child
native routing/capture, exact canonical child request coincidence, strict duplicate/
missing/unknown/label failures, no helper forcing, and clean owned cancellation.
Fake providers are qualification fixtures only, never scientific model observations.
Do not implement a new scheduler or general scripted-agent framework.

If deterministic filter16 retains accuracy while spending meaningfully less total
physical compute on user queries, and free-root behavior misses that opportunity
despite executable competence/mixed strict rewards, propose a small query-varied
root RLVR comparison. Any cost-aware objective must be separately declared; start
with the existing terminal exact reward. If the root already adapts, test new
query compositions or lengths. If interface or child-label failures dominate,
repair that prerequisite in a separately frozen comparison, or retire the planning
claim. Four contexts and answer skew cannot support broad generalization claims.
No new reward, forced helper use, correspondence guarantee, model selection or
launch follows automatically from this document.
