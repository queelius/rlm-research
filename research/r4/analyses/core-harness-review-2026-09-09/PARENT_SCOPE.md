# Harness review: scope and decisions

2026-09-09 00:56 UTC. This is a bounded experimental-validity review, requested
while the independent Prime/nano GPU campaign continues. It is not a production
hardening exercise or a claim that every possible defect has been excluded.

## Core findings and action

The parent read both reported code paths and independently ran the four stored
CPU reproductions: four passed in 0.38 seconds. Two deliberately assert the old
incorrect behavior; they are evidence, not the desired regression expectations.

An isolated worktree was created at
`/project/alex_phd/repos/rlm/.worktrees/core-evidence-fidelity-20260909`, branch
`fix/core-evidence-fidelity-20260909`, starting at
`3aeb99d2a6ff125868f0329bfea584de84c1f715`. The existing observation and ledger
tests passed before changes (21 tests). Focused test-first fixes are underway.

- Preserve known executor-output omissions in the next controller observation.
  Combined counts must include executor loss plus later observation shortening,
  without counting the same missing characters twice. Existing no-loss encoding
  and bounded structural identity must remain intact.
- Record known token usage when a valid response arrives after a deadline,
  without accepting its answer or changing deadline/error precedence. Qualify
  action and run deadlines separately.

No main-branch, frozen experiment source, running service or GPU job is changed
by these fixes. The campaign does not execute these core paths; its results must
not be blamed on these defects.

## Actual experimental runtime checks

The parent separately inspected the native role router, root exporter and
capture wrapper, strict scorer, original task setup, native TrainClient renderer
path, and ACP root-reply handling.

- `OolongTask.setup` writes only the context bytes to `context.txt`. The answer
  remains host-side task data. The prompt construction does not add the gold.
- The actual role router changes the served adapter using invocation depth.
  Source request, native prompt/action token IDs, returned alias and sampling
  seed are checked by the existing exporter. An initially suspected missing
  seed check was ruled out by reading those comparisons.
- `Trace.last_reply` uses `root_reply` when present. ACP assigns that field from
  the root program's reply before handling a returned ACP error. It has a
  last-assistant fallback if root_reply is absent, so the independent optimizer
  reviewer was asked to check admitted campaign records for this case. No
  misattributed reward has been established.
- Strict count scoring uses the declared final-line format. Official scoring is
  diagnostic, not a replacement reward. Correct final counts can still conceal
  omitted records or cancelling classification errors; that is a limitation of
  the task endpoint, not proof of faithful decomposition.
- The inherited nano client can retry certain errors. This source-level
  possibility does not establish retries in an observed long episode, nor does
  an idempotent retry necessarily imply another GPU generation. The two costly
  first-round failures have many recorded child calls; do not label them retry
  backoff without request-level evidence.

A separate reviewer is checking the actual current root-RLVR loss, probability,
optimizer and loading paths. No defect requiring the live campaign to stop has
been established as of this note.

## Useful follow-on checks already prepared

The fixed B checkpoint will receive twelve fresh paired HF calls comparing the
two saved prompt serializations. The parent read the complete driver and ran a
fresh CPU verification successfully (session 42737, exit 0). This tests a known
tool-key-order difference; it does not assume that difference explains failure.

The computed-string submission experiment compares committed bytes against one
extra model restatement after a single shared computation. The parent read its
complete submission, overlay, driver, study and plugin sources. It changes only
new owned containers. Its common task instruction is being clarified before
freezing, and budget infeasibility must remain separate from semantic copying
failure. No answer-file or output-repair fallback is introduced.

## Completion addendum: 2026-09-09 01:44 UTC

Both core fixes are committed as
`bb2d6da11b5a97f8e27e449d095b6fa7c1bcdbd4` on
`fix/core-evidence-fidelity-20260909`. The isolated worktree is clean and retained.
The parent re-read the complete diff, rechecked the four reviewed file hashes,
and reran observation, ledger, late-response and engine tests successfully before
committing. Ruff on the four files and the staged whitespace check passed.
The [independent review](INDEPENDENT_FIX_REVIEW.md) approved the bounded fixes.
No full-suite or merged-main success is claimed: the GPU-first exploratory scope
uses focused verification, and neither a merge nor a push was performed.

The [actual RLVR-path audit](../actual-rlvr-harness-review-2026-09-09/REPORT.md)
found no established optimizer/loss bug, but did reproduce a material exporter
classification defect at round04. A new exclusion-only continuation is prepared
separately; original sources, STOP and three committed updates stay unchanged.
The [computed-answer readout](../mrcr-computed-commit-2026-09-09/REPORT.md) reached
six model episodes but no explicit submissions, so it supplies no paired terminal
comparison. These later results supersede the earlier preparation status above.
