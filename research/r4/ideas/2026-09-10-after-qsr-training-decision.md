---
schema: research-decision-v1
id: idea:after-qsr-training-decision
as_of_utc: "2026-09-10T00:20:00Z"
status: proposed_not_ready_no_implementation
related_questions: ["rq:controller", "rq:reduction"]
evidence_report: "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/query-sensitive-rl-audit-report.md"
evidence_report_sha256: "46ad5bba023639855456ca22e0ea79694391b0cc41d88e5f3e0a47016200843b"
recommended_order:
  - released_ancestor_calibration
  - execution_grounded_operator_warm_start
  - balanced_terminal_reward_control
  - explicit_process_reward_only_for_mechanism
implementation_frozen: false
gpu_authorized: false
---

# What would make more controller training informative?

The query-sensitive RL run made ten genuine Adam updates, but its trained readout improved only on
zero-gold answers, never called a child, and became much less available on ambiguous `all` prompts.
Another unchanged terminal-reward run would mostly retest a known shortcut and interface failure.

## Smallest decision sequence

1. **Calibrate served reference and ancestor policies before training.** The accepted fixed24
   diagnostic compares a served 857 zero-effect-adapter reference, interface checkpoint4, and
   low66c checkpoint8 using clarified scope language and identical tools. It uses the already
   QSR/research-exposed `readout-00` through `readout-03` contexts, not a globally root-unseen panel;
   all child sources are training-exposed. It can test reachability descriptively, but its four
   context clusters and phase-order confound limit inference. If no policy performs authentic
   reductions, deprioritize blind RL and run a minimal interface/reachability or teacher-NLL check
   before deciding whether SFT is warranted; do not retire training from this small panel alone.
2. **Test an execution-grounded operator warm start.** If at least one calibration policy shows the
   primitives, train on a tiny balanced set of complete native trajectories that use actual returned
   child predictions or direct public-record reasoning, maintain live state, execute the requested
   operator, and stop. Preserve wrong child predictions; never insert host labels or answers. Compare
   the warm checkpoint with its ancestor on a fixed disjoint panel before adding RL. A warm start is
   promoted only if nonzero task accuracy and executed reductions improve without availability loss.
3. **Use balanced terminal reward as the practical primary RL control.** Balance zero and nonzero
   answers within operator/scope groups so `Answer: 0` is not a profitable default. Terminal task
   reward should still accept any correct route: direct reasoning can be a legitimate solution, and
   mandatory child calls are not required for task correctness. This tests practical task learning.
4. **Add explicit process reward only for a separate mechanism question.** If the goal is specifically
   acquisition-to-reduction control, compare terminal-only reward with a process arm that credits
   authenticated use of returned content in a query-relevant reduction. Do not reward a tool call,
   file open, variable name, or copied map by itself; those invite ceremonial behavior. Keep terminal
   correctness primary and report process success separately.

The minimal next decision is calibration, not another RL campaign. Only after calibration and the
warm-start comparison pass should a small matched terminal-only versus process-reward study be
frozen. Promotion requires paired nonzero wins across multiple context clusters, executed evidence
use where claimed, and stable availability. Zero-only gains, tool ceremony, all-scope loops, or
improvement confined to exposed contexts should deprioritize repeating the exact recipe unchanged,
not rule out terminal reward or controller training broadly.
