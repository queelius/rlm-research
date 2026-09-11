# Fixed leaf-composition control

Approved parent request, 2026-09-08. CPU preparation only; parent owns service/launch.

Question: with decomposition and aggregation supplied by an operator, how much composition
headroom do the original versus validation-selected SFT leaf weights provide? This is a
fixed-routine control, not autonomous decomposition, discovered planning or a new method.

Use exactly leaf-composition-transfer-v1/prepared-v1/DATA.json, SHA256
1ea4640da5a8e3e305bee7f79d5abeecb02507d6bcc33d709d1c7209fd47bfc2.
Its six disjoint64-question contexts contain384 preselected official-TREC-test groups.
The same questions occur in the component test; they are new compositions, not new source
questions. No component-test outputs are read for selection here. Preserve all48 parent
coordinates: six contexts × HUM/NUM count tasks × two paired seeds × two child weights.
Preserve the parent's counterbalanced coordinate order and exact seeds.

Supply13 source-order batches per coordinate:12 batches of5, then4. Make all624 leaf calls;
do not reuse sampled labels across queries/seeds. Use the frozen leaf72 reconstructed native
system/tools/user-prefix plus its unchanged definitions. Direct HTTP first-response requests,
temperature0.5, top_p1, top_k-1, min_p0, max_tokens256, existing return_token_ids, no new
logprobs or server grammar. The public task target/gold, record IDs and provenance stay
host-side; only question text goes in each leaf input. No root LLM, tool execution, child
filesystem, further agent turns, output repair, retries or fallback.

Four concurrent model calls on one parent-owned dual-LoRA server;900-second client cap
including preflight,30-second per-request timeout; optional external timeout16minutes.
Checkpoint every attempted call atomically, and every coordinate when its13 calls complete.
On infrastructure/routing error stop new dispatch while other in-flight requests finish;
retain partial results and explicit missing coordinates. Never overwrite/relaunch an attempt.
Parent-facing run command requires the actual server directory and frozen role binding.
Verify selection hash/checkpoint, both adapter/config hashes, original base identity,
server-ready/binding metadata and live model-card alias/root/parent paths before requests.
Only SELECTION.json's selected checkpoint may be bound; no test-informed checkpoint choice.
Actual parent service1472413 declares model_dtype=auto and lora_dtype=auto, with BF16
inference casting of both FP32 adapter files. Preserve that common serving representation
and record it explicitly; file identity is not a claim of FP32 inference arithmetic.

Primary aggregate is available only when all13 responses are whole equal-length JSON arrays
of exact canonical labels. Count the predeclared target in operator code and compare with
host gold. Any malformed/noncanonical/tool-output batch makes the aggregate unavailable
and observable strict0. Infrastructure error or unrun work yields null, never invented0.
Report item correctness for aligned arrays separately even when another item invalidates
the whole-array contract; do not silently normalize aliases. Report confusion, unique
question coverage, false positives/negatives, exact count, cancellation, contract failures,
truncations and complete cost. Correct aggregate plus incorrect items is explicitly retained.

Units: six context groups,384 distinct questions,24 paired coordinates. Three thousand
seventy-two requested labels are repeated assignments, not independent questions.
This differs from free-root RLM in supplied control flow and256-versus2048 output caps;
it is composition headroom, not a clean equal-budget causal estimate of removing the root.

Promotion: compare to parent composition48 by exact task/seed/weight coordinates. Better
leaf accuracy without aggregate accuracy supports further semantic/count-error analysis;
a large fixed-versus-free gap identifies root integration headroom. No prompt retuning,
reward-admission change or further model training is part of this sidecar.
