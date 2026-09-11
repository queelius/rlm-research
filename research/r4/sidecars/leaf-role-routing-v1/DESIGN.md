# Frozen-root, supervised-child role experiment

Decision, 2026-09-08 21:49 UTC: implement the smallest inference-only role treatment
while leaf SFT runs. User authorizes autonomous exploratory decisions and focused
tests; this is additive external research code, not a production branch or root repo
API change. No generic worktree/merge ceremony should hold an independent GPU job.

Question: does improving the model that answers delegated classification questions
improve a composed RLM when the root model and prompts are unchanged?

Compare original root/original child versus original root/validation-selected SFT
child. Both adapters share exact Qwen3-4B base/tokenizer. Selected adapter is bound
from trec-leaf-sft-v1/outputs/attempt-001/SELECTION.json after it exists. Never choose
weights based on test outcomes. Load immutable original and SFT aliases together on
one base with max_loras=2; inspect actual paths/hashes/dtypes and forwarded aliases.

Only intervention: every trusted depth1 model call uses the declared child alias;
depth0 always uses original. No schema grammar, prompt rewriting, output repair,
fallback, forced recursion, or root-weight update in this first experiment. Use the
exact definitions-enabled executable example from recursive-label-definitions-v1
in both conditions. It is still an example-supplied decomposition, not plan discovery.

Source inspection reference: ideas/2026-09-08-leaf-contract-routing-inspection.md.
Add an explicit invocation depth/ID signal at pinned nano's model-request boundary.
Route owned request bodies after Prime's global model override. Missing/malformed
role metadata is an observable routing failure, not inferred from prompt content.
Per-request body mutation must agree with saved model call records. Preserve ACP
request linkage, and audit depth, invocation, actual alias, message hash, model hash,
role-map hash, and error/uncommitted calls. No shared session mutation across requests.

Preserve downloaded/shared sources. Implement the pinned nano change only inside
new owned container copies or an additive external fork. Hash original and modified
code; do not mutate existing running/shared environments or frozen helper files.
Generated code stays in qualified rootless runtime. Do not put label maps/gold in
containers. No extra answer-submission features belong in this implementation.

First qualification/comparison: reused development tasks12000008/09/25, two fresh
paired seeds per task, two child choices (12 episodes), fixed root temperature0.5,
full-support knobs and existing2048-token per-call/depth1/no-compaction limits.
Alternate pair order, at most4 paired workers,1800-second study cap. Save each episode
atomically, retain raw outputs and all errors. Freeze coordinates before requests.
This repeated development comparison is mechanism evidence, not generalization.

Next independent composition comparison is prepared separately: six64-record
documents from fixed official-TREC test groups, disjoint from SFT train/validation,
two count queries each, two paired seeds and child choices (48 episodes). Freeze
context partition and queries before inspecting its results. The leaf test questions
also occur in component test evaluation; this is new composition, not unseen source.

Metrics: strict final answer correctness, actual recursion and role-application
coverage, record-level canonical correctness, distinct-record coverage, aggregation
consistency, and final-versus-computed agreement. Report costs including all roots
and children, latency, truncation, malformed-policy outcomes, and infrastructure
failures separately. Do not export mixed-policy EvalClient traces as RLVR data.

Promotion: if child metrics improve but final does not, inspect root coverage and
aggregation; if both improve, repeat on new context compositions/layouts and acquire
a genuinely different labeled source before broad claims. If child competence does
not transfer across prompt/batch shape, compare matching leaf contracts explicitly.
