---
question_id: root-qs6-ag-live-helper-transfer-v1
stage: exploratory_cpu_preparation_main_launch_only
unique_articles: 128
contexts: 8
queries_per_context: 2
episodes: 48
owner_seconds: 1800
external_seconds: 1900
root: fixed_QS6
helper_comparison: c32_vs_original_broader_RL8_seed1
selection: no_best_seed_or_checkpoint
---

# Does the helper gain improve the whole system's final answers?

Each fresh16-article context gets a count and a weight-sum query. Targets rotate through all
four categories twice per family. Three arms share the frozen QS6 root: no-child/Python,
c32 helper, and original broader RL8 seed1 helper. The control is an RLM without a helper,
not the strongest conventional direct-answer baseline. The two helper arms have identical
root prompt tokens and paired seeds; seed2 is not selected as best and is not queried here.

The full16 helper interface makes four **live** canonical B4 calls and joins only their
returned keys. The root chooses whether to use it and writes all aggregation code. It is
prescribed B4 acquisition, not learned grouping or an unrestricted recursive child task.
The logical map wrapper is explicitly not a model sample: it has no fabricated token IDs,
logprobs or usage. Physical helper envelopes supply the actual cost and predictions.

## Data and familiarity

128 articles are hash-ranked from the pinned official AG test remainder, excluding canonical
local helper/root exposures, broader1024+512, prior panels and the newly frozen official512.
The freeze found6894 eligible records. It selects32/class globally, then groups label-blind;
it never puts four/class into every context. Count answers vary1–7, so a constant4 shortcut
is not built in. Positive weights and user identities are label-blind synthetic metadata.
No answer-based resampling occurs. `prepare.build()` reuses the exact saved exclusion snapshot.

QS6 has been trained on these aggregation families with TREC records and authored root
programs. This tests fresh AG task-content transfer, not unseen operators, general planning
or novel RLM architecture. Source pretraining exposure is unknown. Keep news texts outside
Git/publication; the cached source card's research/non-commercial language is not a verified
redistribution license. Host gold is mode0600 and never staged in the runtime. The public
module contains serialization/validation only, not the host reducer or answers.

## Execution and caps

MAIN runs `owner.py run --owner-seconds 1800` with the native Python, inherited private
credential and exactly one GPU, under the shared lock and external timeout1900. No launch
is authorized by READY alone. Outputs are immutable `outputs/attempt-001`.

The existing service permits two simultaneous LoRAs. Phase0 loads QS6+c32 and runs the16
no-child then16 c32 episodes. After verified release, phase1 loads QS6+RL8 and runs16 episodes.
Each arm has400s; each service startup240s; the whole owner reserves90s for cleanup. These
are caps, not promised runtimes. A source predecessor's72 replay-root episodes took801s;
this pilot adds live128 maximum B4 calls and a second service startup. Partial tails remain
unattempted and cannot support a complete-panel promotion.

The root samples atT.5/max2048 with six cumulative logical model turns per episode,
maxdepth0/1, and zero retries. A logical helper wrapper consumes one of those turns while its
four physical B4 calls useT0/max1024 and the exact trained prompt/ordered label schema.
Thus the conservative bound is288 root+128 helper =416 physical calls, not48 calls.
One full16 acquisition is allowed per episode; partial/repeated/custom child requests fail
visibly, with no inferred labels, semantic repairs or saved-map reuse. Root-only solving
remains allowed in both helper arms. Four episodes execute concurrently. Each request and
episode checkpoints immediately. Actual EngineCore batch-invariant proof and clean release
are required; a config flag alone is not runtime qualification.

Maximum initial root prefix+2048 is3043; maximum B4 prefix+1024 is2129, both below8192.
The longest external context is1573 tokenizer tokens, **not** the root's actual prompt cost.
Later root prefixes can exceed limits after tool use: retain context/turn stops explicitly,
never truncate or silently raise caps. Root instruction/tool availability necessarily differs
for the no-child control. Different service phases/cache histories remain a limitation;
paired seeds do not promise bitwise-identical trajectories.

## Readout and next decision

Primary: RL8 versus c32 final exact answers on16 paired queries clustered in8 contexts.
Secondary: each helper arm versus no-child/Python. Report each arm's fixed16 denominator,
available count, malformed/fixed-horizon failures, infrastructure unknowns and unattempted
tail. Do not relabel setup or transport failures as incorrect semantic answers.

Separately report the actual helper's local labels and the exact aggregate implied by each
complete returned map. Compare root final to that map aggregate and to host gold: correct
map/wrong root; wrong map/faithful wrong root; two different wrong aggregates; and compensation
are different findings. These are trace-consistency diagnoses, not proof of what caused a
root answer. Unused helpers and incomplete maps remain explicit, not wrong labels.

Count every root and physical B4 request, token usage, unknown-usage errors, service startup,
cleanup and full owner time; do not multiply a wrapper or charge its four calls twice. Report
cost per arm and root/helper separately. The two questions independently acquire live maps;
there is no cross-episode inference cache or free replay. Training cost is separate.

A complete positive final-answer difference supported across at least two contexts is an
exploratory reason for a fresh-context repeat, not statistical confirmation. If helper maps
improve but final answers do not, inspect root aggregation/faithfulness. If maps do not improve,
do not call this root failure. Ledger, evidence-stop or tighter input-budget variants are only
future proposals when actual traces show coverage/state loss or wasted input; no such variant
or additional training is implemented here. No general-recursion claim follows from this48.

## CPU evidence

The real collector fixture crosses task construction, an owned cached CPU container, two
native root responses, one logical helper invocation and four canonical native B4 responses.
It verifies exact first prefix, ordered schemas, real token decoding/16-ID merge, and causal
root token/node matching. These responses are authored CPU fixtures, not scientific inference.
An early fixture caught the original QS namespace's stale allocation lookup; the new sidecar
now calls the accepted terminal-native runtime closure. It also established that logical
trace.model keeps the caller alias: wrapper exclusion is therefore keyed by authenticated ACP
request IDs, never a guessed model alias. Existing sealed sources and failed receipts are intact.
