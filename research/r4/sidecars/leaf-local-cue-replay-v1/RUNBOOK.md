# Launch only after MAIN acceptance

CPU verification command is READY.verify_argv with CUDA_VISIBLE_DEVICES empty. It authenticates inputs, small sources, pinned versions and prior-hashed model-shard stat identities; no model is loaded. Preparation uses the qualified native interpreter for tokenizer/typed rendering and the training interpreter for tiny CPU causal tests. No new environment or downloads.

READY.launch_argv runs one HF process with MAIN's actual inherited MIG UUID/LD environment, not hardcoded CUDA0. Use900s parent outer cap,750s work with120s cleanup reserve. The direct `outputs/attempt-001` directory must not exist. There are no service workers and no inference endpoint. Do not launch if another owned GPU process is active; MAIN controls serialized handoff.

Artifacts: INPUTS/MODEL_LOADED, atomic units/<id>.json and STATUS. Each condition contains every completed candidate's raw token logprobs and unnormalized sequence score; finite-set normalization only when all candidates complete. A partial unit persists known candidates with normalized probabilitiesNULL. Unrun IDs remain explicitly listed against immutable UNITS. STOP/timeout/error is a result, not authority to resample or resume. No historical logprobs or model outputs are used as likelihood targets.

Read outputs by32 context-position units; four positions are nested in each of eight contexts. The prior gold history is artificial and fixed, not the free-running model's history. Do not pool this HF conditional experiment with sampled vLLM accuracy or interpret the normalized finite-label score as calibrated probability. Preserve the original prompt-error draft and approved neutral amendment.
