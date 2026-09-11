# Meaningful output tags versus placeholder structure

This bounded exploratory follow-up asks whether meaningful identifiers before each
label help beyond extra output structure and token allowance. The primary
comparison is meaningful_tag minus placeholder_tag within each decoding mode.
Anonymous arrays and the earlier ID map bridge to prior studies. This is a leaf
probe, with no training, root inference, or generated-code execution.

The frozen source is grammar160 DATA.json: first four declared TREC contexts and
all four SST contexts, 64 records each. Record text, order, source provenance and
input IDs remain exact. These contexts are developmental/exposed after grammar160,
not an independent test set. Neither labels nor model outcomes select contexts.
The existing old child adapter c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3
and pinned Qwen3-4B-Instruct-2507 base are the only weights.

The 128 calls cross eight contexts, seeds 981264101 and 981264102, four
representations and free/exact-schema decoding. Representations are an anonymous
label array, an input-ID-to-label object, an ordered array of objects with keys
tag then label and corresponding input-ID tags, and the identical object-array
structure with literal q0000 for every tag. q0000 is absent from all input IDs.
Within each representation only structured_outputs differs between free/exact;
system prompt, tools, task definitions and ID-bearing inputs remain common.
Output instructions truthfully differ across representations, including an
explicit explanation of the task-irrelevant placeholder.

The eight cells are cyclically rotated by (context_index*2+repeat) modulo8.
Each cell appears twice at each dispatch position across the study and once per
position within each task. The collector records planned dispatch order and
actual start/end wall times. Four HTTP calls can overlap; order is a submission
counterbalance, not a guarantee of finish order.

Exact schemas enforce all64 positions or IDs, canonical task labels, no extra
properties and exact tags. Ordered arrays use prefixItems and items=false.
Every label position retains the complete canonical label set; no gold label
enters any request or grammar. CPU qualification compiles each unique schema
and validates all128 physical prompts using the pinned vLLM typed tool objects
and native tokenizer template. Free/exact prompt token IDs must agree.

Sampling uses qualified temperature0.5/full-support settings, common3072 output
tokens,8192 context tokens, four concurrent calls,120-second HTTP timeout, no
retries,900-second collection cap and1800-second inclusive owned envelope with
120 seconds reserved for cleanup. All prompts plus output cap must fit before
launch. The wrapper reuses the existing authenticated suite start/release and
child-command lifecycle, providing one old-adapter binding. It creates no new
scheduler and requires main's GPU assignment. No checkpoints are needed.

Raw requests/wire bodies, responses, provider model identity, token IDs when
available, usage including missing cache fields, stop reasons, timing, and
per-call artifacts are retained. Strict parsing rejects malformed JSON,
duplicate keys, cardinality mismatches, wrong tags/IDs, noncanonical labels and
extra properties. No repair, truncation, prefixes, aliases or generated code.
Invalid completed responses earn zero strict correct assignments while semantic
alignment remains unavailable. Infrastructure/unrun coordinates have null
strict scores. Position-wise accuracy, complete-batch correctness, exact label
counts and confusion tables use only complete aligned canonical outputs.

Inference is grouped by four source contexts per task, with seeds and cells
nested. TREC and SST remain separate. If meaningful tags outperform placeholders
with comparable realized lengths, record correspondence becomes more plausible;
similar improvement supports structure/segmented generation. Success only with
exact decoding narrows the result to decoder-supported output. None of these
patterns automatically constitutes a confirmatory claim.

The tokenizer audit fixes tags before inference and tests every canonical label
under compact and ordinary JSON serialization. Even equal synthetic lengths do
not establish equal actual compute or perfectly neutral padding: prompts,
variable labels, serialization and free-response behavior can differ.
