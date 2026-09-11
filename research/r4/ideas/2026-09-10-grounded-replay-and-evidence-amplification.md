---
title: Can replaying the evidence help, or reinforce the wrong evidence?
date: 2026-09-10
status: literature_informed_candidate_not_ready
author: MAIN
gpu_authorized: false
priority: behind_ready_training_and_child_representation_bridges
source:
  url: https://arxiv.org/html/2607.02509v1
  version: v1
  revision_date: 2026-07-02
  retrieved: 2026-09-10
  read_depth: abstract_methods_3_1_to_3_4_appendix_B4_and_E1_assumptions
  license: CC_BY_4_0_as_displayed_by_arxiv_HTML
assets_downloaded: false
official_code_inspected: false
novelty_established: false
---

# Primary source and important distinction

[ReContext](https://arxiv.org/html/2607.02509v1) uses attention-derived proposals
to copy source sentences near the question, retaining the original context.
Later selection rounds condition on previously copied evidence. Its recursion
is this repeated selection, not an RLM tree of delegated model calls. AppendixB4
describes context-cache reuse and two replay rounds. This requires internal
attention access; our current native service is not a ready reproduction.
Neither the empirical results nor implementation have been reproduced here.

The printed theorem assumptions deserve separate scrutiny. AppendixE1 assumes
unit-temperature softmax scores and a positive query-score gap smaller than its
corresponding probability gap. Under those printed definitions that appears
impossible; the derivation below is MAIN's inference, not a claim by the authors.
This concern does not refute the paper's empirical results.

# Local question, not a claim of reproducing ReContext

When an RLM already acquired a complete child-label map, would copying its
relevant entries immediately before the final calculation improve correct use
of that map? Or would replay merely reinforce mistaken child evidence?

Our checkpoint2 audit has32 faithful calculations among43 observable composed
tasks, including5 wrong answers caused by child labels. The agreement study
also shows that repeating a same-model check can preserve wrong labels. These
observations distinguish **using the evidence** from **having correct evidence**.
They do not establish whether replay helps either.

Smallest candidate: a paired continuation from a captured, authenticated
post-acquisition state with an unchanged root model, task and actual child map.
Compare no replay, a source-linked copy of relevant public records plus their
observed labels, and a length-matched copy selected without task relevance.
Never insert reference labels or drop the original evidence. Freeze the cohort
without selecting only failed answers. Use fresh paired seeds. A first pilot
could use24 source states×3arms=72 continuations, one A100,1800s total cap,
with per-case artifacts and a fixed terminal evaluation.

Primary: faithful requested calculation on the observed map; report strict
gold-answer correctness separately, including correct-zero coincidences.
Secondary: whether wrong child labels become harder to recover from, all
input/output/cache costs, and total model calls. A10-point faithful-use gain
across at least6/8 context clusters without availability loss would motivate
a fresh-cohort replication; no strict-answer gain would limit adoption to a
process aid. These provisional gates must be finalized before a runnable seal.

Do not implement yet: first establish a native, reproducible post-acquisition
continuation seam. Replaying text is not equivalent to restoring the Python
session, hidden state, or call tree. If this seam costs more than a bounded CPU
preparation pass, prefer existing ready full-run comparisons. Attention-based
selection is a separate intervention, not something to quietly add here.

# Check on the printed theoretical premise

Write two initial logits as z1>zi, with delta=z1−zi>0. For softmax probabilities,

    p1−pi = (exp(z1)−exp(zi)) / sum_j exp(zj)
           <= (exp(delta)−1) / (exp(delta)+1)
           = tanh(delta/2) < delta/2 < delta.

Thus delta/(p1−pi)>2, not<1 as required by the displayed maximum-ratio premise.
The last strict inequality holds for every positive delta. This is an apparent
vacuity in the printed setup, conditional on the equations as written; a missing
temperature/scale or a corrected premise could alter the situation. No theorem
failure is inferred for a corrected formulation, and no author contact occurred.

Research lesson for us: a relevance signal can repeatedly amplify its initial
mistake. Any empirical replay experiment needs a wrong-evidence stratum and
a matched extra-context control, rather than borrowing a monotonic-improvement
claim as a guarantee.
