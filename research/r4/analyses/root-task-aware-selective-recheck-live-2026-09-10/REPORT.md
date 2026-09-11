---
status: complete_native_audit
date: 2026-09-10
study: root-task-aware-selective-recheck-v1
native_calls: 48
valid_derived_episodes: 32
promotion_gate_passed: false
---

# Task-aware selective recheck audit

The task-aware score changes which errors are reviewed, but neither it nor A/B agreement-abstention
clears the frozen downstream gate. All 48 native calls authenticated as complete and valid, producing
32/32 valid derived episodes with no NULL or observed-invalid cases.

At equal 25% review budget, confidence selected 107/151 initial errors; task-aware selected 78/151.
Confidence-single made 72 repairs and 31 regressions (net +41 labels), while task-aware-single made
41 repairs and 18 regressions (net +23). Task-aware nevertheless reduced aggregate absolute J1 error
under agreement from 92 to 77 and beat confidence-agreement in 5/8 episodes (one loss, two ties),
short of the required 6/8. It produced only 1/8 exact answers versus confidence-single's 2/8, so it
also failed the requirement for two additional exact repairs.

Agreement-abstention was not an effective verifier. For task-aware selection, it changed absolute
J1 error in only one episode (an improvement), tied in seven, and retained 20/320 selected labels.
It left exact accuracy at 1/8. For confidence selection it retained 46/320 labels but increased total
absolute error from 73 to 92 and reduced exact answers from 2/8 to 1/8. A/B agreed on 48 wrong labels
in the task-aware panel and 42 in the confidence panel, directly illustrating correlated error.

| Selection / derived policy | Absolute J1 error sum | Exact J1 | Repairs | Regressions | Net labels | Abstentions |
|---|---:|---:|---:|---:|---:|---:|
| confidence / single A | 73 | 2/8 | 72 | 31 | +41 | 0 |
| confidence / agreement | 92 | 1/8 | 62 | 16 | +46 | 46 |
| task-aware / single A | 81 | 1/8 | 41 | 18 | +23 | 0 |
| task-aware / agreement | 77 | 1/8 | 38 | 15 | +23 | 20 |

## Paired absolute-error effects

Negative values favor the second named method. Task-aware minus confidence was +8 under single A
(2 wins, 2 losses, 4 ties) and -15 under agreement (5 wins, 1 loss, 2 ties). Agreement minus single
was +19 for confidence (0 wins, 4 losses, 4 ties) and -4 for task-aware (1 win, 0 losses, 7 ties).
The descriptive interaction was -23 (four negative, four zero). At size 64, task-aware-agreement's
absolute-error sum was 5 versus confidence-agreement's 11; at size 256 it was 72 versus 81. These
small correlated panels do not support an interaction estimate beyond description.

The gate failed three scientific clauses: task-aware-agreement won only 5/8, agreement beat
task-aware-single only 1/8, and task-aware-agreement did not add two exact repairs over
confidence-single. Validity and cost-balance clauses passed.

## Physical cost and availability

Standalone single A corresponds to 24 physical calls: 38,768 input, 12,428 output, and 19,696 cached
tokens. Consensus requires all 48 A+B calls: 77,536 input, 24,766 output, and 56,992 cached tokens.
Thus its input is exactly twice single's; output is approximately twice, while cache accounting is
not linear across the sequential samples. The full union with the 40 shared ceiling calls counted
once is 88 calls, 148,962 input, 49,395 output, and 94,512 cached tokens. Unknown usage is zero.
Task-aware versus confidence input-plus-output ratio was 0.992. All 48 provider IDs were unique;
owner and parent elapsed times were 119.693 and 120.192 seconds, with authenticated clean release.

The four derived conditions share these physical calls. A/B policies, selection arms, nested sizes,
and episodes are correlated; none are independent replications.

## Ranked research direction

1. Prioritize a genuinely different or better verifier, or a task representation that predicts
   downstream sufficient statistics directly. Same-model A/B agreement preserved many correlated
   mistakes and provided almost no episode-level movement.
2. Retain task-aware sensitivity only as a secondary routing feature: it modestly improved aggregate
   J1 error under agreement despite selecting fewer raw errors, but missed its 6/8 and exact gates.
3. Do not scale confidence-only review or this local worst-case score to new clusters yet. The
   recurring gap is verification/downstream representation, not simply finding more low-confidence
   labels.

These eight episodes are nested within four exposed clusters. Local one-label sensitivity is not
causal influence or expected value of information, and A/B agreement is not calibrated confidence.

Replay: `python audit.py --output /tmp/task-aware-audit`.

