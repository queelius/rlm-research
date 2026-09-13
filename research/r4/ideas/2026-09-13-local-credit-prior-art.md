---
schema: research-idea-v1
id: idea:decision-local-credit-prior-art
created_utc: "2026-09-13T06:43:00Z"
status: primary_sources_read_design_input_not_replication
related_questions: ["rq:rl-effective-feedback", "rq:public-state-and-decision-accounting"]
sources:
  - url: "https://arxiv.org/html/2605.22074v1"
    revision: v1
    published: "2026-05-21"
    read_sections: "3.2, especially 3.2.2"
  - url: "https://arxiv.org/html/2608.13179v1"
    revision: v1
    published: "2026-08-13"
    read_sections: "3.3-3.4 and Appendix A.1-A.2"
retrieved: "2026-09-13"
downloaded_code: false
novelty_claim: false
---

# Give credit to the decision, not every part of the answer

## Relevant existing methods

SCRL assigns separate relative rewards to verifiable subproblem answer spans.
It combines curriculum and original-question rollouts and gates credit by
consecutive solved progress. This makes answer-span credit close prior art,
not a new invention of our experiment. [Primary method](https://arxiv.org/html/2605.22074v1).

CrEST reweights verified turn-level credit using a privileged self-teacher and
gates amplification. Its appendix carefully distinguishes preserving each
token's scalar sign from preserving the aggregate gradient direction. That
distinction cautions against claiming that a local weighting rule guarantees
whole-task improvement. [Primary method and qualification](https://arxiv.org/html/2608.13179v1).

## What these suggest for our own experiment

Our task has separately checkable candidate decisions without needing a teacher
to invent intermediate questions. If the proposed boolean interface works, we
can compare assigning each sampled boolean its own correctness-based relative
credit with assigning the whole answer one score. The first comparison should
use identical frozen rollouts, initial adapter, loss-token population, optimizer
and declared normalization, so credit assignment is the intended difference.
This is our proposed adaptation, not a reproduction of either paper.

Independent candidates have no logical dependency on preceding candidates, so
SCRL's consecutive-progress gate is not appropriate by default. A wrong first
candidate must not erase credit for a correctly classified later candidate.
Likewise, a teacher-based reweighting system is unnecessary for the first pilot:
we already have deterministic candidate labels and want the smallest comparison.

The previous selection reward rose while recall fell. Therefore success must
mean more complete correct sets on new cases, not just a larger reward average.
Report wrong inclusions, omissions, validity, cost, and variation across sampled
answers. Uniform candidate decisions supply no group-relative signal; do not
conceal those zero-contrast groups or repeatedly optimize an uninformative batch.

Conditional small test: after the interface pilot, collect a varied frozen
four-rollout-per-case batch; contrast local versus joint credit with fresh
identical-initialization adapters and a held-out case panel. One A100 is enough;
prepare an exact cap and periodic checkpoint manifest before admission. If the
interface fails, first compare shorter positional IDs or local single-candidate
questions; do not build an elaborate reward system around malformed output.
