---
title: Additive audit binding for new-corpus completion
date: 2026-09-10
status: prospective_before_recovery_readout
recovery: root-question-sensitive-sft-new-corpus-completion-v1
author_overlap: true
---

# Recovery-path amendment

The original fixed audit questions and semantic criteria remain unchanged. Attempt 001 ended after
all 72 teacher captures but before model load because its CPU-only launcher removed CUDA visibility;
it produced no treatment or readout. The accepted recovery reuses those exact 72 pinned teachers,
starts a genuinely fresh Adam state from the same fixed24 adapter, requires exactly six full72
updates, and writes the sole new metadata72 readout under
`root-question-sensitive-sft-new-corpus-completion-v1/outputs/attempt-001`.

The audit must bind checkpoint ancestry and readout artifacts to that recovery path while continuing
to bind the training corpus to the original attempt. Cost has three non-overlapping pieces: the
original 72-request capture, the original failed 18.524-second training subprocess, and recovery
training/readout. The original capture is charged once, not copied into recovery physical totals.
The shared historical baseline and original QS6 are reused and not rerun.

Execution remains conditional on an exact MAIN terminal relay, clean recovery owner release, exact
parent EXIT, all six genuine updates, and a complete native inventory. No recovery outcome existed
or was inspected when this amendment was written; the stable-anchor predecessor was still active.
I authored both producer packages and this reader, so this is a native reconstruction with disclosed
author overlap, not independent implementation validation.
