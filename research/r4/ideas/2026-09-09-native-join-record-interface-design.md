# Native join: record-interface pilot (design only)

2026-09-09. Targeted CPU inspection by runtime_port, not the independent endpoint audit. No implementation, service, GPU, lock, or queue change is authorized by this memo.

## Question and observed motivation

Does truthful machine-readable access help an unchanged root execute the correct purchase join, or must those structured records already be visible inline? This tests a context interface, not a supplied join algorithm.

I inspected all eight actual direct/Python programs and their observations from `sidecars/root-native-partition-join-v1/outputs/attempt-001/rollout/native/episodes`. Every root copied the entire inline sentence dataset into Python; all 12 original/repair literals exactly match their world's 48 source lines after boundary stripping. None loaded the evidence file or called a child. Every program attempted customer-to-product sets followed by both-product membership. Six ended with an observed empty result after bad parsing; two produced the correct nonempty set. Examples: `e177513…` splits on ` purchased ` twice; `7b1cd015…` retains `product N.` but compares `N`; `3a749ed…` repairs a missing `re` import but retains a lowercase-product regex against uppercase products; `471d46b…` changes a failing split into silent skipping. These are actual execution observations, not conclusions from code appearing in a prompt. I did not execute sampled code. Endpoint authentication remains the independent auditor's responsibility.

The old common prompt describes purchase triples even in the sentence-text arm. That is not an explicit false JSON-file claim, but is ambiguous format guidance. A successor should accurately describe every representation; comparison with the old percentage cannot isolate this clarification.

## Smallest recommended comparison: 24 fresh endpoints

Retain **all four existing worlds**, two fresh paired seeds each, three arms. This is an adaptive, previously exposed mechanism panel, not fresh-data generalization. All arms contain the identical 48 facts, original order, customer domain, products and query; no extracted reports, answer/cardinality hints, reordered facts, omitted distractors, precomputed groups, or join code.

| Arm | Inline evidence | File `evidence.dat` |
|---|---|---|
| T | Original purchase sentences | Same sentences |
| F | Same purchase sentences | JSON array of objects with `record_id`, `customer_id`, `product` |
| I | The same JSON objects | Same JSON objects |

Use a common truthful statement that the file contains exactly the same purchase facts as the inline evidence. Describe the actual inline and file formats separately: sentence lines follow `<record_id>: customer <customer_id> purchased product <product>.`; JSON keys contain the three respective string values. No parsing example, import instruction, algorithm, preloaded variable, record accessor, output grammar constraint, or automatic tool call. The original sentence punctuation and capital letters remain unchanged. The filename is common. Host serialization is a lossless schema conversion of all source triples, not a model extraction or gold-conditioned repair.

**Primary F−T:** offering a typed file under identical inline facts. **Secondary I−F:** making the typed representation immediately visible rather than requiring retrieval. All arms have the same actual IPython/native-child inventory, fresh empty REPL, authorized facts and native root harness. Tool availability is held constant, not estimated; accurate format descriptions are common policy, not a fourth factor. Representation-specific truthful descriptions and token lengths necessarily differ: these are interface-package effects, not a pure byte-only causal claim. Historical no-tool results remain descriptive.

Use the prior released **Qwen3-4B-Instruct-2507**, revision `cdbee75f17c01a7cc42f958dc650907174af0554`, no LoRA; optional native children use that same base. Reuse the qualified free-ID vLLM/native lifecycle, renderer and task setup. Root thinking enabled, temperature 0.6/top-p 0.95, 2,560 tokens/action, 8,192-token context; unchanged optional-child configuration. Retain free decoding and the original strict sorted distinct customer-ID JSON-array answer contract. Freeze eight new paired seeds and balanced arm dispatch order before execution; no refill or outcome-selected reruns.

## Measurement, budget and decision

Authenticate actual native final branch, token/model/prompt identity and matching final text. Returned malformed/capped answers are observed failures if invalid; complete strict answers are scored even if capped. Missing/unverified final endpoints remain NULL, separately from invalid zero. Report available accuracy, all-24 operational success and NULL bounds, paired seed-block outcomes nested within four worlds—not 24 independent worlds.

For each actual trace distinguish file load, typed decode, copied literal fidelity, executed grouping/intersection, emitted intermediate result, and final concordance. A file open or correct answer alone is not verified join execution. Charge paid retrieval, repeated literal tokens, optional children, errors/repair calls, wall time and all physical tokens; record host serialization/setup separately. No acquisition is needed for these direct source facts. Equal episodes are not equal token/FLOP budgets.

One A100, four workers, 120 seconds/episode; **1,200 seconds outer = 1,080 work + 90 owned cleanup + 30 outer margin**. Work includes at most 180 seconds startup and 900 for 24 roots/collection. Plan all 24 NULL rows first; preserve every call/episode and partial result on timeout. CPU qualification only: fact/order bijection, truthful native prompts and actual file bytes, common tool inventory, composed owner→service/config→collector CLI, and final-branch scoring regression. Reuse existing qualification rather than a new framework.

Promote F if improved executed joins actually use the typed file. If only I helps and F mostly copies sentences, retrieval/reachability is the next bottleneck. If T itself improves, precise format guidance is a plausible contributor, not isolated proof. If all arms still fail after faithful decoding, inspect reduction/finish transitions before more format work. This is ordinary structured-input/tool-access engineering, not a new join algorithm or evidence of general recursive competence.

## What the 19 incomplete extractions actually lost

Read-only comparison of all 24 returned JSON arrays against original chunks: 24 parseable arrays, all finish `stop`; five exact and 19 omission-only, with **200 missing triples and zero additions**. Fourteen of the 19 retain every requested-product triple. The other five omit six requested-product triples. Across eight complete world/partition report sets, four retain every requested customer/product fact; two more lose nonwinning single-product facts but preserve the join. The remaining two lose one true winner each: world 1/cross loses `c3289`; world 2/colocated loses `c5100`. Thus the host-derived join agrees for **6/8**, but not all query-relevant facts survive and these are not lossless general-purpose reports. This is a privileged source-comparison diagnostic, not an observed root score. All historical exact-source gates and 32 unavailable report endpoints remain unchanged. A later explicitly lossy-report experiment would be a separate question, not part of these 24 calls.

Provenance: original `WORLDS.json` SHA256 `d7ee9d28742aaa6260bc414e114f099ebb888092f1182eb37d176f6cee211bf6`; `protocol.py` SHA256 `6d12052bcdf2b930a8d2f39216d24407e61594c5d4cbb53f0b298c9a886e49c2`. Raw programs and extraction objects remain unmodified under the original attempt. I previously authored reused runtime plumbing, not this scientist driver. This targeted review does not replace its independent full audit.
