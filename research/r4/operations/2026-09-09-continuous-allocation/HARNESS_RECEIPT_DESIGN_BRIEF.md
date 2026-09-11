# Small end-to-end RLM harness modification: source-bound helper receipts

Read-only feasibility/design task, not implementation or GPU launch. Goal: locate
the smallest real seam in the executed Prime/nano/rootless runtime that can test
whether making a helper result easier to consume improves final RLM answers.
The core src/rlm Responses engine is not the experimental runtime; do not conflate them.

Read current findings in analyses/CURRENT_SUMMARY.md, the completed root96 report,
and grammar-training-padding-controls report. Inspect the exact pinned source
behind root-return-contract-factorial-v1 and the current independent-root campaign,
plus the original/lambda/nano comparison under ideas/2026-09-09-official-runtime-comparison.md.
Do not hot-upgrade to a newer upstream or install a repository environment.

Compare two or three genuinely small approaches:

1. An optional parsed/validated result method or field that retains raw text and
   exposes source IDs, labels, missing/duplicate/invalid IDs and visible errors.
2. A separate helper function that explicitly requests an indexed leaf result and
   returns the same receipt without forcing a batching/decomposition plan.
3. A narrower code-native or first-request syntax control if receipt integration
   cannot be scoped to a small source change in the rootless runtime.

Receipt validation must not see correct labels or invent a response fallback.
Do not silently repair malformed JSON, turn unknown failures into negative rewards,
or require all-label evidence when the original task only needs one target count.
Root must remain free to choose queries/decomposition and whether to recover.
Keep task success unchanged; report end-to-end exact success, helper failures,
coverage where meaningful, actual calls/tokens, root syntax and observed consumption.

Return a source-grounded design with exact files/functions/API availability, the
minimal32–64 paired-episode comparison, task/split availability, fixed root/child
choice, expected A100 shape/duration, necessary small integration test, and what
would falsify the benefit. Distinguish a new experiment from a novelty claim; these
ingredients already exist in related work. No broad architecture rewrite. If the
seam is expensive, explain the smallest informative alternative. Cap12minutes,
save DESIGN_PROPOSAL.md beside this brief, and send main the key choice. No
source edits outside that proposal, generated-code host execution, GPU/model/service
calls, process signals, acceptance or further subagents.
