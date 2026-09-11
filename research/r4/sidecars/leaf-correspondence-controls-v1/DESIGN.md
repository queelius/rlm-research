# Leaf correspondence controls v1

Parent-approved CPU preparation only. No GPU/server launch authority.

Weights: exactly old validation-selected child c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3 at trec-leaf-sft-v1/outputs/attempt-001/checkpoint-0128, not either mixed-size curriculum. Base Qwen3-4B-Instruct-2507 cdbee75f17c01a7cc42f958dc650907174af0554. A later immutable endpoint binding must reconcile local bytes and live alias/root/base. No default historical endpoint.

Data: first256 records of validation720's frozen300-record manifest in its existing record_index/question-group-hash order, NOT raw-TREC-line order. Retain original indices, group hashes, representative/all source lines and manifest hashes. Four disjoint64-record contexts;256 unique reused validation questions, not untouched test data. No label-dependent selection, no source-test file/entries consulted. Seeds981261401/402 intentionally paired across both comparisons; prior use checked in SEED_AUDIT.json.

Representation: four contexts × two seeds × three arms =24 calls. Anonymous question list/label array; indexed ID-to-question input/ID-to-label output; indexed input/ID-to-{question,label} output. Echo question is an unconstrained generated string, not a grammar constant/enum of known inputs. Exact canonical-label enums and complete cardinality/ID coverage throughout. Copy fidelity and question-before-label ordering are separate adherence metrics, not semantic repairs. All arms max_tokens3072. Whole representation-plus-constraint treatment, NOT a pure index ablation.

Rotation: four contexts × two seeds × offsets0/16/32/48 =32 calls. Anonymous question/label arrays, exact64 cardinality, max_tokens1024. Left-rotate declared source order; invert on host for question scoring. No voting. Record source/input/output positions separately.

Preserve native system, definitions, tools and sampling. Only user output instructions, representation, schema and specified caps differ. T=.5,top_p1,top_k-1,min_p0,parallel_tool_calls=false,cache_salt0,return_token_ids=true. No extra logprobs, tool execution, retry, alias repair or fallback.

Four workers;60-second call timeout;300-second total live preflight/collection cap per comparison. Atomic checkpoint each call. Keep raw response text/object, provider physical prompt/output IDs, all logical/cached/uncached input and completion costs, errors/unrun coordinates. Missing/duplicate IDs, wrong representation/cardinality and invalid JSON are unaligned, never repaired. Noncanonical strings remain explicitly wrong and invalidate the whole contract. Copy mismatch alone does not change label correctness.

CPU qualification validates actual vLLM ChatCompletionRequest objects, compiles distinct schemas with XGrammar against the frozen tokenizer and checks input+cap<8192. Network-boundary tests use the real inherited collector. Runtime version/models gates and provider physical-input diagnostics distinguish CPU support from actual GPU enforcement.

Freeze inputs/source and both unbound specs; READY last. Parent supplies a truthful endpoint and launches. Existing sources, audits, curricula, campaign, shared queue and Git branch stay unchanged.

