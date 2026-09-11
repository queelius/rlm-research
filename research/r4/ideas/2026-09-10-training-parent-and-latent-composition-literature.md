---
schema: research-idea-v1
id: idea:training-parent-and-latent-composition
as_of_utc: "2026-09-10T00:23:00Z"
status: literature_informed_proposals_not_ready
gpu_authorized: false
related_questions: ["rq:controller", "rq:reduction", "rq:latent-recursion"]
primary_sources:
  - url: "https://arxiv.org/html/2608.28458v1"
    submitted: "2026-08-28"
    read_depth: "Introduction,methods3.1–3.3,mainresults/discussion,AppendixA.4–A.6 and plain-Wordle discussion; not a repository/checkpoint reproduction or complete table audit."
  - url: "https://arxiv.org/html/2608.18171v1"
    submitted: "2026-08-17"
    read_depth: "Introduction,formalism3,model/SFTsetup4.1 and benchmark definitions; not full architecture appendix, full numerical result audit or code reproduction."
acquisition: "Web primary texts only. No code, model, dataset or environment acquired."
decision_boundary: "Does not change frozen CE/MNLI/reference studies or authorize additional training."
---

# Training history matters; architectural recurrence is a separate question

## A relevant small-agent training account

[Acquire, Repair, Preserve](https://arxiv.org/html/2608.28458v1) reports broad
Qwen3.5-2B dialogue-game SFT followed by local preference repair and weight-delta
selection. Its strongest consistent repair result is narrowly localized; later
preference updates vary by evaluation setup. The authors explicitly disclose two
nominal stages that made no weight update, identify the adapter/optimizer causes,
and distinguish corrected reruns. They also report a matched4B off-policy SFT
regression and limited out-of-domain transfer. Whole-dialogue preference tuning
damaged protocol compliance. The broad-SFT corpus is9,522 rows; this is not evidence
that repeating a few dozen narrow traces will teach general interaction. Those are
the paper's reported results, not our replication.

**Implication for us:** calibration should name the actual starting weights. Our
QSR run did make ten updates, but our unchanged comparator was already narrowly
trained. Continue checking numerical changes without mistaking them for capability
gains. Before expanding training, compare a small diverse-corpus option with merely
repeating the current routine. A local next-action preference study is worth proposing
only after identifying an actual, reproducible decision failure; it is not an automatic
improvement over terminal reward or SFT.

Smallest informative comparison: hold start, native contract and readout fixed; vary
training-corpus breadth under reported target/forward-token budgets. Keep a fixed
nonzero-answer and free-execution readout. GPU shape: current4B+fixedchild on the existing
single40GB A100, sequential capture then LoRA training then paired readout. Duration must
be projected from measured capture/forward cost, not from update count. Promote breadth
if gains cross contexts/query structures without collapse or excessive calls; if only
familiar output routines improve, narrow the claim and change the corpus.

## Related latent-composition work, not an immediate harness patch

[Looped Language Models Improve Compositional Tool Calling](https://arxiv.org/html/2608.18171v1)
separates individual calls, independent multi-call sets and output-to-input dependency
chains. Its controlled setup uses Hermes-format SFT, native Ouro models and same-family
retrofitted/nonrecurrent parents. Reported training uses an80GB A100. Ouro and retrofits
use distinct recurrence objectives; recurrence is not implemented by rerunning arbitrary
blocks of an ordinary instruction model. In the described BFCL subset, “Multiple” means
choosing one tool among candidates, whereas NESTful explicitly tests dependent calls.
We have not reproduced these architectures or verified the complete result tables.

**Implication for us:** several calls are not by themselves evidence of decomposition.
Measure which returned values are used by subsequent computation. This directly motivates
our executed-dataflow accounting. A future looped-backbone versus explicit-recursion study
must separate architecture/training from external search and match real compute, not just
parameter count. It remains lower priority than the current native-harness bottlenecks;
our40GB GPU is not automatically sufficient for their80GB recipe.

Smallest future screen: one qualified released looped checkpoint, fixed shallow/dependent
tool tasks, fixed versus adaptive internal depth, with a matched nonlooped reference and
the same external-call allowance. Freeze source/license/checkpoint and measure peak memory
on CPU-qualified entry before assigning a GPU cap. No such executable job is ready now.

## Link to the user's ideas

`new-ideas/ideas.md` was read completely; it remains unmodified. Its key distinction
survives these papers: a Python-capable RLM can already express many proposed strategies.
The contribution would be an interface or learned policy that makes useful composition
reliable and efficient, not merely more recursion. The most immediate open question is
still whether our model can acquire the right evidence, carry it into an actual operator,
and stop—on more than a few familiar examples.
