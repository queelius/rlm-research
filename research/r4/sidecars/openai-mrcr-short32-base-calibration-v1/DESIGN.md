# OpenAI MRCR short32 base calibration

This is a bounded signal-calibration campaign over the first eight records in the frozen
`DATA_READY_V2` training order, with four rollouts per record. The 16 frozen held-out
records receive no model queries and do not affect selection, thresholds, prompts, or
scores. Verifying the parent data closure may read their hashes and protected manifest;
it does not expose them to the model or this campaign's scorer.

Each task receives its exact original JSON document as read-only `/context.json` plus the
exact final question. The root prompt discloses only the file, representation, byte size,
generic Python/RLM capabilities, and response requirement. It contains no target index,
needle position, parser recipe, or answer. Root and children are the same unadapted
Qwen3-4B policy. Temperature is 0.5, maximum generation is 2,048 tokens per call, depth
is one, and the harness allows at most six completed returned turns cumulatively across
root and children. Collector and harness retries are both zero; the V7 audit wrapper adds
no model attempt.

The OpenAI scorer is the pinned `grade(response, answer, random_string_to_prepend)` source.
Valid terminal replies receive that continuous score. A turn/budget-limited or invalid
terminal is reward zero only if at least one root action returned with exact tokens and
logprobs, every returned root/child action maps to the causal trace, and no infrastructure
error is present. Setup, mount, serialization, transport, missing-token, or ambiguous
mapping failures remain unavailable and make the calibration ineligible.

The prospective root-RL gate is an exact 32-record inventory, all 32 scientifically
available, zero infrastructure-unavailable records, at least two mixed G4 groups, mean
reward below 0.90, the six-turn cap respected, and clean owner release. Delegated versus
nondelegated trajectory summaries are observational diagnostics, not a causal comparison.
The campaign is not a generalization test and says nothing about base-pretraining exposure.

Caps are initially 600 seconds science, 900 seconds owner, and 1,000 seconds external.
`READY.json` cannot be created until the actual repaired V7 run completes 32 episodes with
returned-native evidence inside 600 seconds. If it exceeds that bound, a new additive cap
revision is required rather than silently changing this contract.
