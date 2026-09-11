---
schema: bounded-research-decision-note-v1
id: evidence-use-versus-evidence-preservation
date: 2026-09-10
status: conditional_proposal_not_implemented
research_questions: ["rq:controller", "rq:sufficient-interface"]
primary_sources:
  - url: "https://arxiv.org/html/2606.02373v1"
    title: "Harness-1"
    read_depth: "Introduction and sections2.1–2.3 reread; already in local literature record. Not a fresh code audit."
  - url: "https://arxiv.org/html/2606.05263v1"
    title: "Policy-Conditioned Counterfactual Credit"
    read_depth: "Methods3.1–3.4, tables1–5, robustness4.4–4.5 and AppendixA.2; not reproduced. No project repository identified in the inspected HTML."
local_sources:
  - "analyses/root-qs-scale-harness-factorial-live-2026-09-10/MAIN_ADOPTION.json"
  - "analyses/root-qs-scale-harness-factorial-live-2026-09-10/ADOPTION_ADDENDUM_SEAL.json"
  - "ideas/2026-09-10-typed-evidence-harness-followups.md"
gpu_authority: none
---

# Preserve evidence first; then ask whether the model uses it

The new scale audit supplies a concrete warning. A returned child map, a decoded
map in Python, and a correct final answer are different events. Six of seven
correct-and-performed successes were zero-answer cases. Two used reducers that
worked on the realized empty support but would fail on nonempty selected records.
Those facts motivate both nonzero-support reporting and stronger future tests of
evidence use. They do not establish intentional reward exploitation.

## Relevant prior work changes the novelty boundary

Harness-1 already externalizes search bookkeeping and trains a model to make
semantic decisions over rendered state. Its SFT and RL share the observation
renderer; its terminal reward combines several shaped signals. Therefore an
external map store alone is not a convincing novelty claim, nor is this paper
evidence that our unchanged sparse reward will learn to use one.
[Primary methods](https://arxiv.org/html/2606.02373v1).

The counterfactual-credit paper distinguishes deleting a step, paraphrasing it,
substituting evidence and perturbing tool output. It evaluates continuations under
a frozen policy and explicitly limits the causal interpretation to the chosen
intervention and continuation policy. Its implementation includes nuisance models,
validity checks and multiple reward components; the described training uses
3,000 updates and multiple continuations per selected step. I have not reproduced
its empirical claims or located runnable project code in the inspected paper.
The relevant idea for us is the need for a well-defined intervention and a control
with the same extra information and computation, not adopting the full algorithm.
[Methods and implementation notes](https://arxiv.org/html/2606.05263v1).

## A small, distinct follow-up if the memory test works

Question: when the root receives a complete predicted-label map, does its final
calculation depend on the task-relevant entries, or does it continue with a fixed
routine or answer? This is separate from asking whether the labels match reality.

After a typed-state intervention actually improves acquisition and reduction,
freeze eight nonzero-answer context/question blocks and four state interventions:
unchanged map; formatting-only permutation preserving every key/value association;
one task-relevant category substitution; and one category substitution that leaves
the requested aggregate unchanged. Define substitutions from public task rules
and the frozen predicted map before sampling continuations, not from their outcomes.
The host computes an explicitly named map-consistent counterfactual answer; it is
not the original dataset answer and must never replace that score.

Use matched frozen root weights and paired seeds, the same root-visible interface,
and exactly one continuation per block/arm initially:32 endpoints on one A10040GB,
180-second endpoint caps and at most2,400 seconds including startup and cleanup.
This is a prospective envelope, not measured throughput. Save original and changed
maps, intervention rules, exact prefixes, native completions, code observations,
costs and all unavailable outcomes. Use the normal controlled research runtime;
do not run extracted model programs as unsandboxed offline analysis scripts.

Primary diagnostics: stability under formatting-only changes, unchanged answers
under aggregate-preserving substitutions, and correctly changed computations under
aggregate-changing substitutions. Report pairs and context groups, not independent
token decisions. Require at least6/8 blocks to satisfy all three checks with no
availability loss before considering a larger new-context study. This is an
exploratory decision threshold, not a significance claim. Retire the intervention
as a credit signal if it mostly induces format failure, implausible states or
generic copying; do not turn it directly into a reward before that check.

## Immediate priority

No extra GPU work is requested by this note. The accepted queue remains RL readout,
fresh-context numbering, and the supplied-plan diagnostic, with child-contract SFT
and the exact-group memory-efficient RL recovery being prepared. Those results
must determine whether this more elaborate evidence-use study is warranted.
