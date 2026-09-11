---
id: question-sensitive-sft-new-corpus-completion-v1
status: prospective_recovery
date: 2026-09-10
---

# New-corpus QS SFT completion

The original attempt captured all 72 planned, authenticated teacher trajectories, then failed
before model load because its inherited subprocess helper deliberately removed CUDA visibility.
This additive recovery reuses that immutable complete corpus once. It performs the originally
planned six full-corpus updates from the same fixed24 adapter with a genuinely fresh Adam state,
then runs the same frozen metadata72 readout. It does not recapture, rerank, replace, or repair any
teacher; it does not rerun the shared baseline or the original QS6 comparator.

The only operative change is infrastructure: training is launched by the qualified owned-process
pattern while preserving MAIN's single assigned GPU. The original failed attempt and its costs
remain separate. The recovery has 3,000 seconds outer / 2,970 owned / 2,850 work: at most 1,200 for
training, 1,500 for service plus readout, 150 finalization, 120 release reserve, and 30 outer margin.

Primary interpretation remains the frozen original question: does a new, disjoint training corpus
reproduce the metadata72 improvement of the first QS6 realization? Exact answers are not credited as
faithful computation without native program/observation review. This is one new corpus realization
on a research-exposed readout, not a pristine replication.
