# Broad16 stopped on an unrecognized child context-boundary rejection

Diagnosis only, September9,2026. No frozen source, raw episode, export, reward,
checkpoint, service or GPU state changed. No failed call was converted into a
training example. The original STOP remains authoritative.

## Ruling

The blocking calls are **unsampled child requests at exactly8192 prompt tokens**,
not root requests, an observed model-alias corruption, or a server outage. The
frozen exclusion amendment recognizes only the other vLLM branch: prompt length
strictly greater than8192. It rejects the exact-limit error message before its
length check, and its existing `len(ids) <= 8192` rejection would also need a
narrow second branch. Do not solve this with an unrestricted HTTP400 exemption.

The original exporter was rerun read-only/in-memory against the preserved24
episodes. It found21 admitted outcomes,9 successes and3 excluded episodes. All
six failed calls across those three episodes are depth1, exact fixed child c32de,
HTTP400/BadRequestError, without a sampled node, usage, or native completion.
There are619 successful returned audits and6 error audits; no other error family
was observed in these24 captures.

## Exact failure and source assumption

The decisive episode is
`bc2608598befba7a342f6caed172da6b37296829eda6eaae31b51e51e09d63c8`,
task `training-016-00:human_being`, repeat7, seed1183836357. Its three failed
request IDs are:

- `7a48db3d21624954a2e0dd151b897d78` (trace call54)
- `369a2426f5c04b9f8232a5c3b39878bb` (trace call107)
- `6655a03d58924f85b01496ed95a37ac5` (trace call160)

Each wire request has8192 actual integer token IDs, child alias
`strict-rlm-qwen3-4b-role-sft-selected-v1`, model SHA
`c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`,
and the correct role-map digest. Native wire/call/audit aliases agree. Sampling
is the frozen temperature0.5/top_p1/top_k−1/min_p0, max_tokens2048, logprobs1,
return_token_ids=true, skip_special_tokens=false, stop IDs151645/151643,
seed1183836357; optional routed_experts_prompt_start is8110 and within the prompt.

The raw wire body is an error-only JSON envelope, typeBadRequestError/code400,
HTTP400, with this exact message:

> The decoder prompt (length 8192) plus the number of requested output tokens (at least 1) is longer than the maximum model length of 8192. Make sure that `max_model_len` is no smaller than the number of text tokens (prompt + requested output tokens).

In [the frozen amendment](../../sidecars/root-recovered-child-continuation-v1/native_amendment.py),
`REJECTION` at line18 recognizes only the shorter “prompt ... is longer” form;
`verify_failed_call` raises at line48, with an additional strict-length condition
at line53. The exact unmodified function accepted all three >8192 failures below
and rejected all three equality failures with the observed STOP message.

The installed vLLM source independently explains both messages:
`/project/alex_phd/envs/prime-rl-5990b1b/lib/python3.12/site-packages/vllm/v1/engine/input_processor.py`
lines419–448. It first rejects `prompt_len > max_prompt_len`, then separately
rejects equality for a generate runner because at least one output token needs
space. This is pre-generation input validation; the error-only response and
absence of a sampled node/completion agree with that classification.

## All implicated episodes and causal evidence

All paths below are relative to
`sidecars/root-broad-curriculum-v1/outputs/attempt-001/round-01/collection/`.

| Episode prefix | Failed child lengths | Successful calls checked | Root turns/tokens in diagnostic projection | Endpoint / existing training reward |
| --- | --- | ---: | ---: | --- |
| 06b816719944… | 9492,9682 | 237 | 5 /1659 | wrong valid terminal /null |
| bc2608598bef… | 8192,8192,8192 | 167 | 7 /3601 | wrong invalid terminal /null |
| fe197cdef3f4… | 9789 | 105 | 4 /1520 | wrong valid terminal /null |

For diagnosis only, each episode was deep-copied in memory, only its unsampled
failed-call entries were omitted, and the **untouched** root exporter
`episode_turns` was run against the original routing audit directory and binding.
All original graph nodes remained byte-equivalent. All successful calls retained
their sampled-node correspondence, graph reachability, physical causal prefix,
token masks/logprobs, sampling seeds, actual model and role linkage. Successful
plus failed request counts exactly recover239,170 and106 calls respectively.
No tokens/nodes were removed and none of these recovered root actions were admitted.

The other21 episodes passed the original exporter without this diagnostic
projection; their admitted root-action total is11922 tokens and child-evidence
total7868 tokens. The combined check accounts for all619 successful calls.
There is no evidence here of dropped **sampled causal tokens** causing export
failure. This does not claim that every pre-render intended character in a failed
request was independently reconstructed; actual failed wire IDs are retained,
and the affected entire episodes remain excluded under the proposed remedy.
Three rejected attempts are not three sampled inferences. No500, timeout,
connection loss, or root-role rejection was found in the recorded failure set.

## Smallest scientifically valid continuation

Propose a new immutable exclusion-only amendment/continuation, after parent ruling:

1. Keep the existing >8192 rule untouched. Add only the exact vLLM equality
   error family, requiring the error-only400 envelope and its declared prompt
   length to equal both actual wire-ID count and8192. Preserve every existing
   request-ID, child-depth, fixed-weight/alias/role-map, sampling and no-completion
   check. Root rejection remains outside this child-only rule.
2. Preserve all24 rows' existing fields byte-for-byte before adding exclusion
   certificates. Keep all three affected training rewards null and turns empty;
   their endpoint outcomes remain wrong, separately valid/invalid as observed.
   Do not newly admit recovered trajectories, invent logprobs, or remove graph
   nodes. Unknown failure families still stop the campaign.
3. Rebuild a new export from the same24 raw records and original source spec;
   authenticate the original validation0 export and retain its16 outcomes.
   Bind both old and new artifact hashes plus the preserved STOP in an explicit
   continuation identity. No reroll or validation replay is needed.
4. The unchanged admitted rewards give mixed groups of7 episodes for the16-record
   human task (6correct/1wrong) and8 for the32-record numeric task (3correct/5wrong).
   The64-record group has6 admitted wrong and2 excluded, so is nonmixed and must
   not enter this update. Expected first update:15 episodes, with advantages
   recomputed by the unchanged within-prompt population-standardization rule.
   This is a denominator deduction, not a new GROUP artifact or completed update.
5. Resume original root857a with empty Adam/RNG training state at step0, perform
   exactly one update from that authenticated fresh generation, then continue
   the already frozen round2–16 curriculum. No fresh rollout generation is needed
   for round1 because no optimizer update occurred. Do not silently restart the
   five-hour budget: record1170.54s already spent and parent-approved remaining
   work/cleanup budget separately from the intervening GPU job.

Validation0 remains5/16 endpoint successes;15 outcomes were admitted and one was
already excluded by the existing rule. Reuse, do not upgrade its denominator or
replace its trajectories. The comparison remains exploratory and exclusion of
long/errorful child trajectories is a known selection limitation, not evidence
that orchestration is competent on those trajectories.

## Narrow qualification before accepting such an amendment

Use the three actual8192 audit/call pairs as RED fixtures for the old rule and
positive fixtures for the exact equality branch. Preserve acceptance of the
three actual >8192 pairs. Require negative fixtures for changed length/limit,
8191 or mismatched IDs, root depth/alias, other400/500 message, changed seed or
sampling, non-null sampled node/usage/completion, response with choices, missing
request binding or role-map hash. Test original-versus-new24 row field identity,
all three excluded rewards/turns unchanged, zero graph-node removal, exact
successful/failed partition, and the15-episode mixed group. This is a small
CPU fixture/export check, not a GPU rerun or permission to broaden admission.

## Evidence hashes

- STOP `STOP-118ee771bbdd4646a801f8dd2f7c73b8.json`:
  `21dbe62c328f028f07b002e30409e20afe159f8c17f6cc57934a8b2df223f274`.
- Round1 `rollout/SPEC.json`:
  `c0d048d56ae295a52b75e6eb3d17436fcfc90bdbea63fd8fcf46304e45ac1637`.
- Validation0 `export/MANIFEST.json`:
  `de6c7b21e41ea8c4ca795f1097263c74c2fad8d823819355b8371d90bcb04b3d`.
- Frozen `native_amendment.py`:
  `718ed07886e05c4ddcaaad06edda54fe1db017b2fa17cb525232fd9224ddc491`.
- Installed vLLM `input_processor.py`:
  `f9a7946a16acc2374ff2bdfc22f212cb43461d9ef4d99c5e19a536339f11212f`.
- Decisive `rollout/episodes/bc2608598befba7a342f6caed172da6b37296829eda6eaae31b51e51e09d63c8.json`:
  `ca2dd40a6f2b18db86f956abe7f4a565a8a4db35e5d792f1fc19bf394f357db8`.
- Its three `rollout-routing/role-audit/*-result.json` files:
  `42e0462ac7ad48cdac49c572c88f3e70` → `3126d3f2188a85dbafecf62a46cde70bd39384174e511ea75072ead84f99e32e`;
  `e842bb91afab4a84b7d1500425e646e1` → `e6ab7f62a26f1d7a8d8f33f7cf05fc2ba105cc57a5d863ccca6bb89ea08e74a0`;
  `e299bf3c0fb24dbca39ba8b2ac058172` → `0383cfb44069b798c435ce5bf8f45dfa8328240056c1eda729e44b42a2e02445`.
- Other episode files06b816… andfe197c…:
  `e33152a186e0c18d515811168c7132332cbab933cfe77e6734477bf3daf88cf7`;
  `aa95a4c0235afd733d764d6581fba5a3007a3dfb05fbda6a322119a930ba3682`.

Read-only CPU verification ran in the existing Prime interpreter with CUDA hidden
and bytecode disabled; original rebuild plus all diagnostic graph checks exited0.
No corrected export or training group was written by this diagnosis.
