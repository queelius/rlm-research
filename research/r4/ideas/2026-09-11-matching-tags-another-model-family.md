---
id: idea:matching-tags-another-model-family
date: 2026-09-11
status: acquisition_then_cpu_qualification
question: Does the matching-tag gain appear outside the Qwen family?
planned_gpu: one A10040GB
proposed_calls: 144
proposed_outer_seconds: 2400
gpu_authority: none_until_ready_and_main_acceptance
---

# Move beyond two related models

The completed Qwen4B/8B comparison supports the interface effect within one model
family. Another Qwen checkpoint would do little to address that limit. A useful
next comparison is the same16 input groups, three reference conditions and three
formats (plain labels, row numbers, arbitrary tags) with Mistral-7B-Instruct-v0.3.
The within-model contrast is primary; comparisons of model accuracy are descriptive.
This uses exposed input groups to isolate a new model family, not new-input evidence.

The [official model card](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3)
identifies a seven-billion-parameter instruction-tuned model with an Apache2.0
license. The current public, ungated revision is
`c170c708c41dac9275d15a8fff4eca08d52bab71`, verified through the HF API on September11.
It is selected for a separate family and manageable one-A100 memory, not because
it is the newest model. No model results are claimed.

Acquire only the Transformers safetensors shards, configuration, tokenizer and
model card; omit the duplicate consolidated weights. Keep files under the external
model cache, pin upstream revision and LFS checksums, and record actual local hashes.
Do not execute repository code or enable trust_remote_code. Acquisition overlaps
the active GPU job and does not displace the already queued comparisons.

Before any run, qualify the actual Mistral chat template, end-of-sequence tokens,
native request/response parser, schemas, context length and one nonempty collector
fixture. The existing Qwen-specific token assumptions must not be reused silently.
Proposed cap is144 calls and2400 seconds; freeze seeds, sampling and all rendered
prompts before launch. An early qualification failure is not a negative model result.

Primary: paired later32-label accuracy gain of each tagged format over plain labels,
reported over16 input clusters with missing-outcome bounds and native token costs.
A positive gain in at least12/16 inputs without an availability loss motivates
fresh-input replication; a failure narrows the result and prompts inspection of
format validity versus semantic errors. Numerical promotion rules and all inputs
must be frozen in the eventual runnable package, not chosen after outcomes.
