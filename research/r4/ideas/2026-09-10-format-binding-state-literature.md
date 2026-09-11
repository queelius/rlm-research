---
schema_version: "rlm-literature-to-experiment-v1"
id: "lit:format-binding-state-20260910"
updated_utc: "2026-09-10T02:44:00Z"
status: "primary_methods_read_with_explicit_depth"
related_questions: ["rq:correspondence", "rq:reduction", "rq:controller", "rq:continuation"]
research_lane: "exploratory"
sources:
  - "https://arxiv.org/html/2608.25358v1"
  - "https://arxiv.org/html/2603.03305v1"
  - "https://arxiv.org/html/2310.17191v2"
  - "https://arxiv.org/html/2608.23552v1"
acquisition_manifest: "../acquisitions/2026-09-10-prime-agent.json"
---

# Correct format, correct reference, and usable state are different problems

This is a methods-informed research note, not a systematic review. The source
descriptions below are deliberately bounded. Proposed experiments and interpretations
are our inferences, not reported results of the cited papers.

## Structured-output training already separates format from content

[Where vs What](https://arxiv.org/html/2608.25358v1) distinguishes valid structure,
correct field paths, values in the right locations, and values appearing somewhere.
Its JSON experiments report substantial gains from reward training; its table
results remain much weaker despite better format compliance. AppendixF describes
500 GRPO steps with a Qwen2.5-7B LoRA and a3,400-prompt mixture. The SFT comparison
uses2,907 best-of-ten selected examples; equal optimizer updates, target tokens and
FLOPs are not established by these settings. MAIN read the relevant methods/results
and AppendixF, not every appendix. Our NLI labels are computed semantic judgments,
not the paper's planted-value copying task. Format-versus-content failure is prior
art; the candidate contribution is the controlled effect of a misleading visible
reference despite exact output tags.

## A semantic draft can precede format projection, but it costs extra computation

[Draft-Conditioned Constrained Decoding](https://arxiv.org/html/2603.03305v1)
first obtains an unconstrained draft and then generates a constrained answer
conditioned on it. Its feasible-probability analysis concerns prefix-wise masking,
not global conditioning on all valid complete sequences. The evaluation covers
arithmetic and logical reasoning with several open models. Equal candidate counts
or sums of model parameter counts are not equal realized tokens, calls or FLOPs;
the test-time-scaling comparison includes multiple drafts followed by projection.
MAIN read the algorithm, main experimental setup/results and cost discussion;
the linked code has not been inspected. A correct draft is an assumption in some
arguments, not a guarantee. Our matching-ID benefit also means that constraints
are not uniformly harmful.

## Behavioral ID effects are not yet an internal binding mechanism

[How do Language Models Bind Entities in Context?](https://arxiv.org/html/2310.17191v2)
uses causal activation interventions to study entity–attribute binding, primarily
with LLaMA30B on constructed entity tasks. Its tests distinguish stored binding
information from downstream reconstruction and probe independence from token
position. MAIN read the introduction, causal-mediation setup, factorization and
position experiments, and the start of additivity; later results, appendices and
code were not reviewed. The proposed internal binding vectors are not the same
object as our emitted hexadecimal identifiers. Following a misleading ID in
behavior does not identify the paper's internal mechanism. Any future activation
study would need its own causal controls and a separately pinned model/runtime.

## External state and adaptive harnesses are established RLM ideas

[Prime Agent](https://arxiv.org/html/2608.23552v1) describes persistent execution
state, external history and memory, asynchronous subagents, and versioned harness
adaptation while model weights remain fixed. External state must become visible
to affect a model response; some objects require reconstruction. MAIN read the
main design, experiment sections and discussion, not appendices. Published external
benchmark reference scores are not clean causal harness controls, and its
frontier-model results do not establish the same effects for our4B model.
The official MIT repository was cloned without execution or installation; exact
revision and read depth are in the acquisition manifest. Current HEAD uses a
CPython REPL whereas the paper describes IPython, so HEAD is not assumed to be
the evaluation implementation. Generic persistence, memory and external files
are not claims of novelty for our work.

## Ranked experiments enabled by this reading

1. **Replicate the wrong-visible-reference effect on new contexts.** Compare
   matching, shifted-visible and unrelated tags with all tags exact and labels
   free. Use a fixed public split and label-blind selection, new paired seeds,
   context-level effects and explicit exposure inventories. One40GB A100,
   roughly5–15minutes for48–96 native calls. Promote the mechanism candidate if
   the unrelated condition again removes most of the shifted deficit across
   new context clusters; revise if this is restricted to the exposed panel.
2. **Test voluntary recovery of original evidence.** The already accepted
   canonical-loader48 holds historical maps, data files and model policies fixed.
   The treatment only offers fresh copies, not a reduction algorithm. One A100,
   anticipated5–15minutes,30-minute hard outer cap. Separate actual access,
   faithful calculation, source errors and final answers. Uptake without improved
   recovery would motivate training or an observation-interface change, not more
   claims about persistence alone.
3. **Separate semantic decision from tag projection.** A prospective draft
   comparison could ask whether an initial label-only decision resists a later
   misleading-ID requirement. Charge every additional native draft and projection;
   include a clearly specified matched-budget comparator. One A100,
   approximately10–20minutes for a small paired panel. It is only a candidate,
   not an accepted job or a currently available implementation. Retire the idea
   if any apparent gain is explained by extra sampling or copying privileged
   correct labels.

Training remains a separate prerequisite. The completed six-pass operator SFT has
lower teacher loss but no free child acquisition. A fixed longer continuation with
teacher-context first-action probes can test residual fitting versus failure to
initiate the routine. Neither this literature nor our existing data licenses
claiming that lower loss, tool mentions, map reads, or correct zero answers
demonstrate learned decomposition.
