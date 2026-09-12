# Conditional MRCR root-only update contract

Status: **CPU preflight design only; no optimizer or GPU launch is authorized.** The attempt-004
calibration must first finish and pass its already-frozen gate. It contains eight questions, four
rollouts each, but only one underlying research-exposed context; it can establish optimization
plumbing and within-context signal, not transfer.

## Frozen policy and evidence boundary

- Behavior root and child are the unadapted Qwen3-4B checkpoint at revision
  `cdbee75f17c01a7cc42f958dc650907174af0554`, sampled at temperature 0.5, top-p 1,
  top-k -1, min-p 0, at most 2048 completion tokens per call and six total root+child calls.
- The proposed trainable root is a newly initialized LoRA on that same base: rank 8, alpha 16,
  dropout 0, bias none, targets `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj`.
  Standard PEFT initialization must leave every LoRA B matrix zero, and a before-training logits
  check must show that enabling the adapter does not alter the HF base logits. The child remains
  the native no-adapter base and receives no loss, optimizer parameter, or checkpoint mutation.
- Host official MRCR score is the only reward. Within each exact row's four rollouts,
  `A_i = r_i - mean(r_j, j != i)`. Unavailable outcomes abort; equal-score groups remain in the
  inventory with zero advantage. No answer or document bytes enter model training metadata beyond
  what was already causally observed in the rollout.

## Exact action extraction

For every physical model call, follow the sampled node's `parent` pointers to the WireTrace root,
reverse the chain, and concatenate every node's `token_ids`. The current node's mask must be an
exact nonempty suffix. Its causal prefix is the concatenated sequence minus that suffix; labels are
`-100` on the prefix and the sampled IDs on the suffix. This is why comparing an isolated sampled
node (for example 109 tokens) with a full first prompt (about 1,159 tokens) is invalid.

Root versus child is derived from authenticated semantic edges: `subagent_call` increments depth,
`continuation` preserves it, and `subagent_return` decrements it; multiple edges must agree. Every
graph turn is then matched one-to-one to a saved native response using exact prompt IDs, completion
IDs, and processed completion log-probabilities—not filenames or counts. Any ambiguous/unmatched
call aborts. Only depth-zero suffixes receive loss. Child outputs, tool observations, renderer
framing tokens, and graph control nodes stay in later causal prefixes but are masked from loss.

`extract_inputs.py` is the CPU implementation of these primitives. Its actual recursive trace
fixture identifies root nodes 2/7/9 and child node 5 and reconstructs all four usage lengths.

## Objective and importance correction

For a terminal-return autoregressive root policy, the on-policy score-function term is

`-(1/N) sum_i A_i sum_{t in root turns} sum_k log pi_theta(a_itk | causal prefix_itk)`.

Sequence sum is essential: averaging each turn or token changes trajectory-length weighting. A
fixed child policy is environment dynamics, so its likelihood factor cancels between target and
behavior; child tokens must not enter either the root score or importance ratio.

Because saved behavior log-probabilities are native processed probabilities while training uses HF,
the pre-step forward divides HF logits by 0.5 and gathers the exact root action IDs. The exact
trajectory ratio is

`w_i = exp(sum over every root action token (log pi_HF - log mu_native))`.

Per-turn ratios are not full-trajectory importance sampling. Existing capped token-TIS is a useful
but biased local surrogate and cannot be called an unbiased trajectory correction. The first
proposal therefore only proceeds if detached, unclipped full-trajectory ratios are finite and
supported, with a prospectively frozen ESS/max-weight gate; otherwise it records `NO_UPDATE` and
requires a separately approved biased-surrogate experiment. No threshold should be chosen after
seeing the ratios.

If qualified, the one-step estimator is

`L = -(1/32) sum_i stopgrad(w_i A_i) sum_root_tokens log pi_theta`.

Run dropout off, fresh AdamW, LR 1e-5, weight decay 0, gradient clip 1, exactly one step. Before
`optimizer.step`, re-run the differentiable path and require its gathered current log-probabilities
to match the qualification path within a frozen tolerance, with finite nonzero gradient. Save the
adapter, optimizer, Python/NumPy/Torch RNG, input manifest, qualification, gradient receipt, and
commit atomically. A failed gate or check must save a diagnostic with zero optimizer steps.

## Promotion and limits

The update is worth running only if attempt-004 has at least two mixed groups, mean score below
0.90, clean protocol/release, and at least one independently confirmed successful `/context.txt`
read (the latter is supplementary runtime evidence, not a rewritten science gate). Even a valid
update is a one-context calibration. A learning claim requires later collection and evaluation on
independent underlying MRCR contexts; different length prefixes or questions over the same document
are not independent contexts.

