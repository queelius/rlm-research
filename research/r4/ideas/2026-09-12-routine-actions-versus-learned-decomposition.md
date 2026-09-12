---
schema: rlm-research-idea-v1
created_utc: "2026-09-12T11:54:00Z"
status: conditional_proposal_not_gpu_ready
question: Does removing routine action rendering reveal better decomposition choices?
source:
  url: https://arxiv.org/html/2608.16447v2
  revision: v2
  revision_date: "2026-08-24"
  read_scope: Sections3.1–3.4 and4.1–4.3; abstract and release statement; no code executed.
acquisitions: none
priority: after_interface_qualifier_and_broader_data_RL_readouts
---

# Separate choosing the work from writing the routine code

## What the paper contributes

HaReCAP compiles successful leaf actions into a fixed rule library. Rules may
replace a leaf model call only when the current task and legal-action set support
an unambiguous action; otherwise the original model acts. It leaves recursive
planning in place. Its main environments are Robotouille and ALFWorld, not our
semantic classification tasks. The headline cost reductions concern tasks both
methods solve; the paper also reports full-task results. Those denominators
must not be confused. ALFWorld uses a newly built library, so that comparison
shows portability of the construction method, not zero-shot transfer of the
same rules. The paper says code will be released upon publication; this review
does not establish a usable release. [Primary methods and experiments](https://arxiv.org/html/2608.16447v2).

## Why it is relevant locally

Our optional-helper pilot made many invalid Python calls and attempted imports
of an already-global function. Those failures can conceal useful choices about
what work to delegate. However, they followed a prompt change with fixed weights;
they are not evidence of post-RL control-token collapse. Earlier tool-RL papers
were already reviewed in
[our September10 note](2026-09-10-after-operator-sft-rlvr-options.md).

First run the small explicit-interface qualifier already in preparation. If it
works, vague interface instructions—not a missing execution mechanism—may be
the immediate issue. Do not build a larger architecture just to repair that.

## A conditional experiment of our own

If failures remain concentrated in routine syntax, compare two truthful action
interfaces with fixed model weights and identical raw evidence access. One lets
the model write Python. The other lets it choose explicit operations and input
handles from a small declared library; a deterministic interpreter performs
exactly that operation. For example, the model could choose which record IDs to
send to a helper and then request a count over the returned map. No host labels,
correct answer, inferred missing arguments or answer fallback are supplied.
The library supplies an execution primitive, not the choice of decomposition.

This changes the action space and removes some code-generation burden. A gain
would therefore not establish improved neural reasoning by itself. Measure
both final correctness and whether the model chooses appropriate inputs,
uses actual returned evidence, and handles withheld combinations of known
operations. Include a strong explicit-Python-instruction baseline, not the
error-heavy neutral-prompt pilot alone.

Smallest proposed screen:12 fixed development tasks ×2interfaces, one seed,
one A10040GB,1200s total; save every action, chosen IDs, input/output handles,
actual calls/tokens, failures and available finals. Freeze any rules from
training trajectories only. A promising complete paired gain with fewer
interface errors would justify fresh contexts and unseen operation combinations.
No gain over clear Python instructions would retire this implementation lead.
These numbers are a proposal; exact inputs, source, seed and owner still need
to be sealed before any launch.

## Limits on novelty and transfer

Rule reuse and structured action interfaces have substantial prior art. A
publishable contribution would need a narrower, supported finding about the
interaction between action representation, learned delegation and composition
transfer. Do not replace semantic leaf classification with a cached answer and
call that learned decomposition. Report the cost of building the library and
all evaluated tasks, including failures, in addition to any paired-success cost.
