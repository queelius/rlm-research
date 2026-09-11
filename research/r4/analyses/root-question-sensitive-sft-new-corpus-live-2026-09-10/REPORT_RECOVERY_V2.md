---
title: New-corpus question-sensitive SFT6 completion audit
status: terminal, incomplete readout retained with NULL bounds
date: 2026-09-11
---

# Result

Training the same six-update recipe on a separately selected 72-example corpus again produced a large improvement over the released starting policy on the research-exposed 72-question metadata panel. It did not yield a fully complete evaluation: 70 answers are authenticated and two physically attempted episodes timed out without a result, so the run remains incomplete and the primary score is **57/72 observed, bounded 57–59/72**.

On the 70 available endpoints, every run made a genuine child-model acquisition. Reading every executed program and its matched observations found that **64/70 actually performed the requested operator, category, scope, and threshold**, and **55/70 were both faithful and exactly correct**. The six contrary paths are retained: two correct answers came from summing where the question asked for a per-user maximum; four wrong paths used the wrong operator/category logic or never completed a reduction.

| Panel stratum | Available | Strict correct | Faithful performed | Faithful + correct |
|---|---:|---:|---:|---:|
| All 72 | 70 | 57 | 64 | 55 |
| Primitive 24 | 24 | 19 | 24 | 19 |
| Composed 48 | 46 | 38 | 40 | 36 |
| Nonzero 44 | 43 | 31 | 38 | 29 |
| Zero 28 | 27 | 26 | 26 | 26 |

# Matched interpretation

The unchanged released policy previously scored 17/72 with 17 NULLs (bounds 17–34). The original-corpus QS6 policy scored 53/72 with no NULLs; its sealed semantic review found 62 requested computations and 50 faithful exact answers. The new-corpus run therefore gives **57–59 versus 53** strict answers and **55–57 versus 50** faithful exact answers after accounting for its two unknown endpoints. On the 70 jointly observed original/new endpoints there were seven strict wins, one loss, and 62 ties. The strict gain was concentrated in composed questions: 38–40/48 versus 35/48; primitives were 19/24 versus 18/24.

This is useful replication evidence that the training recipe's large improvement over the released model was not confined to one particular 72-example corpus. It is not an independent test panel or a clean estimate of corpus diversity: both policies are single training realizations, use the same fixed starting adapter and task generator, and are evaluated on the same eight research-exposed contexts. The modest new-versus-original difference should not be treated as superiority of the new corpus.

# Execution and failure accounting

The immutable corpus contains 72 genuine c32 acquisitions. Training started from adapter `94022838…`, fresh Adam, and committed exactly six full-corpus updates: 432 example exposures, 1,296 root-turn exposures, and 101,436 supervised target-token exposures. The fixed checkpoint-6 adapter is `0fdd2c31…`; no validation or best-checkpoint selection occurred.

The original capture attempt made 72 child requests (90,171 input and 17,855 output tokens) and is charged once. Its failed training startup and the first completion's failed training startup are also retained. Completion V2 made 319 readout model attempts: 318 HTTP 200 and one HTTP 400, with known usage of 510,559 input, 41,977 output, and 469,104 cached tokens; one attempt has unknown usage. Both missing endpoints were started, not unrun: index 15 made 18 calls and ended after a backend HTTP 400 plus harness timeout; index 34 made three HTTP-200 calls and then timed out. Neither is repaired or inferred.

# Claim boundary and next comparison

The strongest claim is narrow: six full-corpus supervised updates reliably move this Qwen3-4B root policy from weak acquisition/reduction toward frequent genuine child use and correct task-specific computation on this exposed interface. Remaining failures still include child-label errors and six operator/execution mistakes. A publishable generalization claim needs the same fixed recipe evaluated on genuinely new root contexts, preferably with multiple independently captured training corpora or seeds; another comparison on these eight contexts would mostly measure sampling stability.

The audit was written by the package/recovery author after terminal relay. The incomplete-readout rule was frozen before scores were opened. Sampled code was inspected with its recorded observations and was never reexecuted.
