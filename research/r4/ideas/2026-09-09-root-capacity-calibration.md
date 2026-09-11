---
schema: research-decision-v1
id: idea:root-capacity-calibration
reviewed_utc: "2026-09-09T23:11:13Z"
status: proposed_not_READY_no_weights_acquired
related_questions: ["rq:controller", "rq:reduction", "rq:sufficient-interface"]
priority: conditional_after_interface_and_query_sensitive_readouts
assets_acquired: []
---

# Check a stronger starting model before interpreting a small-model ceiling

The current experiments use a4B controller. Failures may reflect the interface,
training distribution or starting model; they do not establish that RLM
decomposition itself cannot work. A larger released policy would provide a useful
capacity calibration if the clearer-interface and query-sensitive readouts remain
weak. Do not use this proposal to displace accepted GPU jobs or blindly add epochs.

## Primary model metadata inspected

The official Qwen3-8B card supports explicit thinking/non-thinking modes and gives
tool-use guidance. The public HF API currently resolves it to
`b968826d9c46dd6066d109eabc6255188de91218`, Apache-2.0, ungated, with
8,190,735,360 BF16 parameters. Raw parameter storage is approximately16.38GB before
runtime, activations or KV cache. This is a storage calculation, not an observed
A100 peak. Its Qwen3 format is closer to the qualified native path than Qwen3.5's
different tool syntax. [Official card](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/README.md),
[metadata API](https://huggingface.co/api/models/Qwen/Qwen3-8B?blobs=true).

The official Qwen3.5-9B card describes a hybrid language/vision model, text-only
serving and a Qwen3-coder tool parser. Current revision is
`c202236235762e1c871ad0ccb60c8ee5ba337b9a`, Apache-2.0, ungated; API storage totals
9,653,100,528 BF16 and3,840 FP32 parameters (approximately19.31GB). Its maximum
advertised context is not a claim that that context fits our40GB GPU. New native
tool/rendering qualification is required; the existing4B leaf result is not proof
of9B native-root compatibility. [Official card](https://huggingface.co/Qwen/Qwen3.5-9B/blob/c202236235762e1c871ad0ccb60c8ee5ba337b9a/README.md),
[metadata API](https://huggingface.co/api/models/Qwen/Qwen3.5-9B?blobs=true).

Read depth: model/config metadata and selected overview, serving, thinking and
tool-use passages. Not a benchmark reproduction, license legal opinion, or complete
paper/model-card review. No new weights, dependencies or environments were acquired.

## Smallest informative calibration

Prefer one8B released-policy comparison if it becomes decision-relevant. Freeze
the same source facts, final contract, tool inventory, context/output caps and two
paired seeds on a small panel containing both source-access and nontrivial
combination tasks. Include a contemporaneous released4B baseline; a historical
SFT4B versus released8B comparison alone would conflate training and model choice.
Use a documented common thinking setting and truthful templates, not transplanted
token IDs. Preserve all failed native endpoints, real programs/observations and
measured costs. No root/child switch hidden behind an unchanged model alias.

Provisional envelope: one A10040GB, sequential model owners, at most48 native
endpoints and45minutes outer after pinned download/CPU qualification. Model-source
hashes, exact panel, seeds and lifecycle are not frozen yet. If optional children
also change, report a whole-model package comparison rather than isolated root
size. Equal endpoint caps do not imply equal tokens, FLOPs or historical training.

Promotion: a stronger released model consistently performs real scoped operations
where4B fails, on the same facts, suggests moving subsequent controller learning
to a stronger initialization. Similar parser/uptake failures across both instead
prioritize the interface. If both solve the clearer interface, do not train merely
to produce another checkpoint; expand to genuinely harder held-out compositions.
Cross-size gains would not by themselves establish a scaling law or novel method.
