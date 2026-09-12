# Review amendment: corrected decision logic and cached MRCR inventory

This amendment supersedes only the points below. `DECISION.md` and `DECISION.yaml` remain unchanged
as the original reviewed proposal. No trainer, evaluator, queue entry, or GPU process was created.

## Corrections to the decision memo

1. **Other-question credit was described too loosely.** With exact binary rewards, an all-wrong
   action has reward zero and the mean reward of the other questions is nonnegative. Its
   other-question-centered advantage is therefore nonpositive, never positive. The alternative can
   push sampled wrong sequences down, but it does not identify or demonstrate a correct action.
   Cross-question difficulty changes baselines, magnitudes, variance, and sample weights; it is not
   teacher feedback. The empirical conclusion remains: 32/32 groups having nonzero signal instead
   of 5/32 did not change any of the 256 evaluated labels.

2. **The proposed context count was internally inconsistent.** A claim requiring gains in two held
   contexts requires at least five genuinely distinct contexts: three training and two held. With
   only one held context, the result is limited held-context transfer evidence. It is not literally
   “no generalization,” but it cannot establish replication across independent held contexts.

3. **The root runtime projection was unsupported.** 3,900 seconds is 65 minutes, not 39 minutes.
   More importantly, that cap covers collection, one update, and two evaluation services; it is not
   a measured 32-trajectory acquisition time. Multiplying it by four to forecast 2.6 hours was
   invalid. A larger study must budget collection, replay/training, and each evaluation service from
   their actual calibration receipts. Until those exist, there is no defensible total runtime
   forecast in this proposal.

4. **The TREC interface qualifier is not a hard prerequisite for MRCR.** It tests the QS6/TREC
   recursive ABI. The independent no-adapter MRCR runtime can remain informative if its own traces
   authenticate context inspection, protocol integrity, observability, and clean release. A TREC
   qualifier failure should block training through that TREC interface, not an otherwise valid MRCR
   calibration.

5. **Do not replace the frozen MRCR calibration gate after seeing its design.** The current
   prospective gate is at least 2 mixed groups and mean official score below 0.90, together with its
   existing protocol/inspection requirements. The suggested 4/8 threshold was not the frozen gate
   and must not be applied retrospectively. A later, separately frozen multi-context study may set a
   stricter prospective gate before observing those outcomes.

6. **Revise the helper-learning dose.** If the AG direction survives its queued qualification, the
   meaningful comparison should use eight steps with 128 newly distinct examples per step (1,024
   distinct examples total), not another four-step reuse of 128 total examples. Compare RL and SFT
   from the same c32 start on the same 1,024-item inventory. The rollout group size, action-token
   denominator, and caps must be frozen in that later design; this amendment does not invent them.
   The matched SFT arm remains essential. The old same-32 T2/LR10x/other31 variants remain retired.

## Cached MRCR context inventory

I streamed all five cached CSVs (757 rows, about 1.80 GB) without changing them. For every row,
`queries` ended exactly in `view_ops`; removing that final query yields the underlying prompt
context. Hashing those bytes produced **10 exact contexts**, not five:

| Cached object | Rows | Exact contexts | Rows per context |
|---|---:|---:|---|
| 2-needle, 4K--8K | 82 | 6 | 10, 10, 12, 12, 14, 24 |
| 2-needle, 32K--64K | 121 | 1 | 121 |
| 8-needle, 64K--128K | 103 | 1 | 103 |
| 8-needle, 128K--256K | 141 | 1 | 141 |
| 8-needle, 512K--1M | 310 | 1 | 310 |

Different long-length filenames are not independent corpora. After splitting exact `User` /
`Assistant` turns, the 512K--1M context shares 168/174 turns with the 32K--64K context, 306/314
with the 64K--128K context, and 609/620 with the 128K--256K context. None is a literal character
prefix of another because the few-shot header/order differs, but the substantive turn overlap is
near-subsumption (96.6%, 97.5%, and 98.2% of the shorter turn sets). Target rows within each of these
objects are variants over that one context.

There is one immediately usable **small-context** 3-train/2-held inventory. Five of the six 4K--8K
contexts can be chosen with zero exact conversation-turn overlap among them:

- `5abc8460cee4...`: 12 rows, 6,540--6,541 tokens;
- `c256805ce4fc...`: 10 rows, 4,511--4,513 tokens;
- `cdb24d4bcfc...`: 10 rows, 6,278--6,280 tokens;
- `cf7216dfd4ad...`: 12 rows, 5,702--5,705 tokens;
- `eaeac5ed1756...`: 24 rows, 8,170--8,175 tokens.

The omitted sixth context, `cb0f74db704d...`, shares two exact turns with `eaeac5ed1756...` (all
other pairs in the selected five share zero). Every selected context has at least ten official
target rows. This can support a prospectively frozen 3-context-train/2-context-held procedure test,
but only at 4K--8K. It does **not** establish long-context transfer, and these public synthetic
contexts may still share generation sources or base-pretraining exposure. The cache currently lacks
five content-independent contexts at 32K or longer.

## Revised decision boundary

- Run the existing MRCR calibration under its own frozen gate; do not condition it on the TREC
  qualifier.
- If the question is a fast proof of procedure transfer, the five content-disjoint 4K--8K contexts
  can support 3 train / 2 held, with the limitation stated prominently.
- If the claim requires long-context procedure generalization, the current cache is insufficient.
  Acquire or construct additional official-compatible, content-disjoint long contexts before
  designing the learning run; length buckets from the cached family cannot serve as independent
  splits.
- For helper learning, prefer the future 8 x 128 fresh-item RL-versus-SFT comparison over any more
  one-step or repeated-32 mechanics.

## Reproducibility notes

- Cache manifest SHA-256: `175fcdca4b6db955c1ad37688cfad4e9064b7112223d05dc6ba8c4dba7036c4d`.
- 4K--8K object SHA-256: `81f5e08995cbf2c1d55947a80cb71ce1a62743819c0b48b85b4d4d3b30e725f5`.
- The full inventory pass checked 757/757 exact final-query suffixes. The hash/count pass took 24.6
  CPU seconds; the independent turn-overlap pass took 24.1 CPU seconds.
