# Correspondence → whole-RLM: two ranked next tests

2026-09-09. Design-only focused scouting, not implementation/acceptance. MAIN supplied the latest mechanism summary; no queued fresh96 or plan-SFT outcomes were inspected. Matching cues work across tasks/models, but sparse/phase effects identify local behavioral dependence, not attention or freely learned ID retrieval: the grammar supplies those tags.

## Literature that changes the decision

Five primary sources inspected on2026-09-09, selected sections/abstracts—not exhaustive novelty review:

1. [Cheng etal., Batch Prompting, §2.2](https://aclanthology.org/2023.emnlp-industry.74.pdf), EMNLP Industry, December2023 (publisher gives month): indexed input/output correspondence and parsing were already explicit design goals. IDs/batching alone are not new.
2. [Lin etal., BatchPrompt v3](https://arxiv.org/html/2309.00384v3),2024-07-15: batch order/position sensitivity and permutation ensembling are established. They motivate fixing input order and separating item accuracy from histogram accuracy.
3. [Park etal., Grammar-Aligned Decoding v4](https://arxiv.org/html/2405.21047v4),2026-09-02: grammar masking can distort generation distributions. Different schemas are different child action spaces, not merely helpful wording; we are not implementing their ASAp algorithm.
4. [Patel etal., LOTUS v1](https://arxiv.org/html/2407.11418v1),2024-07-16, §§2–3: semantic operators separate a logical query/API from physical execution. A fixed map API with alternative child representations fits this established abstraction.
5. [Zhang etal., RLM v3](https://arxiv.org/html/2512.24601v3),2026-05-11, §2: external state, recursive calls and subsequent observations jointly determine behavior. Component gains need an actual continuation test; no general RLM novelty claim follows.

## 1. Preferred: hide generation representation, preserve the root API

32 whole-RLM episodes: fixed low66cce root+c32de child × four existing held-out-training contexts (query_transfer00/01, length_transfer00/01) × two tasks × two fresh seeds × two child representations. These320 source groups are exposed developmental evaluation data, disjoint from384 training groups. Retain exact records/order/public metadata; no training. Tasks: existing global count; and identify the first display-order record of the public target category among eight hash-selected public IDs, returning its numeric ID suffix or0ifabsent. Both use familiar strict `Answer: N`, avoiding a new root JSON-output requirement. ID subsets are frozen label-independently; report no-match/constant-answer baselines without rebalancing. Identity answers expose misassignments global counts can conceal.

Both arms expose unchanged `request_for(batch)` / `strict_map(child.answer, ids)`. For exact source-bound direct-child requests only, A generates an exact-length label array; B generates an ordered ID→label map. Both grammars require canonical labels. Deterministically zip A's labels to **requested order**, never inferred/gold order; serialize both returned maps identically. Preserve genuine misassignments/misclassifications. Wrong length/schema or unavailable results remain explicit failures, with no fallback/retry/repair. Other child requests remain untreated.

Minimal prospective seam: owned nano `SessionTreeSupervisor._run_child` around `engine.run(prompt)` and broker return; pinned supervisor SHA1b9a1b30… is already located by `root-accumulation-ledger-v1/overlay.py`. Authenticate public ID+text and trusted parent/depth; alter only child output instructions/schema. Existing `typed-helper-child-v1/hooks.py` captures actual nested native sampling. Preserve raw child completion/graph; adapt the **broker result**, not TrainClient sampled tokens/logprobs. The subsequent root observation contains the actual canonical map before native capture. No root prompt/weight/grammar/loss changes, ledger or forced helper uptake. New invocation-bound matcher/round-trip and graph fixtures are required before approval; this seam is feasible, not implemented.

Primary: paired record-identity exactness; count exactness separately, not pooled. Report root syntax, eligible calls/batch sizes, child item accuracy/count-L1, coverage, final consumption and all32/null denominators. Fewer than eight eligible coordinate pairs makes the whole-policy mechanism underexposed, not disproved; do not force/reselect episodes afterward. Direct solutions or small selective batches remain valid. Promote if record-specific benefit appears in multiple contexts with native child improvement and useful whole-task success. If child improves without root benefit, prioritize aggregation/transition fidelity, not more indexing grids.

One A100, symmetric immutable image8cfe, four concurrent episodes;1500s collection/1650work/1770owned/1800outer. Measure every root/child/cached/uncached/output token and failed attempt; no equal-compute claim. Proposed master981326001/seeds011/021; balanced pair order, same-seed intent—not guaranteed trajectories.

## 2. Cheaper mechanism discriminator: deliberately wrong forced reminders

72 calls:12 exposed64-record contexts (four/task: TREC/SST/AG) × two seeds × matching/constant/shifted cues, fixed c32 child. Hold record order and common positional-label instructions fixed; schema forces each shifted cue to name source position(i+17)mod64. Matching/shifted use exactly the same ID-token multiset; constant is the existing shape control. Audit actual tokens/cost, not presumed equality.

Displayed-position correctness remains primary. Separately predeclare named-record alignment, their difference, per-task/context profiles and histogram-L1; never rescue primary scores. Greater shifted named-record alignment supports source-cue following; preserved positional benefit despite wrong names favors generic varying-token/position assistance. Mixed/absent effects narrow the account. The cue is deliberately contradictory, not a neutral counter or attention intervention.

One A100,600s collection/750work/870owned/900outer; proposed981327001/seeds011/021. Bounded manifest scan found neither proposed namespace; recheck before freeze. Both proposals preserve observed-invalid0 versus unavailableNULL, no outcome-selected contexts, and no historical pooling.
