---
title: Advisor-ready takeaways from sparse RL continuation
date: 2026-09-10
status: complete
---

# One-slide version

- **Question:** Do four more terminal-reward RL updates improve a root model that already learned to
  call a fixed classification child?
- **Answer:** No on this fixed exploratory panel. Exact answers fell from 55/72 at the unchanged
  start to 47/72 at checkpoint 6; paired missing-data bounds remain negative (-9 to -5).
- **Mechanism:** Child acquisition remained common (42/45 available composed cases), but only 32/45
  performed the requested calculation and only 26/45 were both faithful and correct. Four exact
  zero answers were coincidences from wrong computations.
- **Meaning:** Optimization was real; behavioral improvement was not. End-answer reward cannot
  distinguish the observed wrong zero computations from genuine successes; whether that drove the
  decline is untested.
- **Claim limit:** One 4B model, one learning rate/reward/curriculum, exposed contexts. This argues
  against repeating the same recipe, not against RL or RLM training in general.
- **Next decision:** Replicate the stronger supervised result on a disjoint training corpus, then
  compare it with a redesigned RL curriculum using a precommitted semantic readout.

# Likely advisor questions

**Could missing outputs explain the drop?** No. Even granting every missing checkpoint-6 result as a
win and every missing start result as a loss leaves the paired net between -9 and -5.

**Did training actually happen?** Yes. Four new Adam updates were committed from checkpoint 2 to 6;
optimizer/RNG/checkpoint lineage was checked. This separates a scientific negative from a failed run.

**Is 47/72 still evidence of useful behavior?** It is evidence of some capability, but not learning
from this continuation. The unchanged policy scored 55/72 on the exact same coordinates.

**Why inspect code instead of only accuracy?** Because four strict-correct composed answers used the
wrong operation and landed on zero by coincidence. End-answer accuracy alone overstates mechanism.

**What would change the conclusion?** A precommitted disjoint-context replication showing a positive
paired effect with faithful acquisition, requested computation, and stopping—not merely lower loss.
