# Child-call amplification: bounded posthoc diagnosis

2026-09-09, CPU-only; four deliberately selected costly, excluded BROAD16 episodes. No generated code was executed, no source/admission/reward was changed, and no GPU or process was queried. This is a mechanism example, not a prevalence or treatment estimate.

The main cost is real agent activity inside children, amplified by root restarts—not deeper recursion. The four episodes contain 150 distinct child invocations but 648 child model calls, plus 22 root calls. Children request Python on 499 sampled turns. A tool-request count is not automatically a count of successful executions. All 670 calls have trusted depth 0 or 1 and kind `ordinary`; no depth-2 calls, checkpoint or compaction calls appear. These four episodes account for 670/862 physical attempts in the stopped run; the three training episodes account for 515/625 training attempts.

| Episode prefix | Root calls | Child invocations | Child calls | Child tool-request turns | Longest child | Unsampled child errors |
|---|---:|---:|---:|---:|---:|---:|
| validation `4c521e61` | 6 | 29 | 149 | 120 | 26 | 5 |
| training `06b81671` | 5 | 64 | 234 | 171 | 63 | 2 |
| training `bc260859` | 7 | 11 | 163 | 152 | 47 | 3 |
| training `fe197cde` | 4 | 46 | 102 | 56 | 9 | 1 |

Each physical request was matched through its real ACP request ID to the recorded trusted invocation/depth audit. Audit bytes were checked against the already sealed STOP analysis hashes once for this projection. The machine evidence retains every selected action, invocation, physical source/hash and semantic dispatch edge. It does not execute or repair code.

## Concrete failure loop

In `bc260859`, the root asks a child to classify the answer type of “What nationality is Ileana Cotrubas ?” (trace nodes 18/223). The child instead writes code to extract the nationality and imports `langchain_core`. The recorded tool observations at nodes 20/121/225 report `ModuleNotFoundError`. Three separate child invocations each issue 46 Python-tool requests; the next physical request is rejected at exactly 8192 prompt tokens. Their first prompts are only 749 tokens. Root-observed exception tracebacks are at nodes 110/211/315.

The root’s next messages (111/212/316) blame a long original prompt or long records, reduce batching/definitions, and restart. Thus both mechanisms are visible: a child keeps attempting irrelevant code after an actual tool error, and the root reacts to the eventual context error by repeating earlier dispatch work. The message at node 316 speculates that records themselves are very long; the captured 749-token initial child request disproves that explanation for this child. This is an error-attribution mismatch, not missing transport evidence.

Other examples corroborate the policy mismatch:

- `06b81671`: child invocation `903455be2ff647e7bc875aea0f9ddce8` has 63 model calls/62 tool requests. It starts with an NLTK import (node 161), receives a missing-package error (162), then repeatedly requests NLTK downloads. Prompt length grows from 776 to 8166. The last sampled response is structurally empty; this is retained, not repaired into a label.
- `4c521e61`: one child starts at 749 tokens, tries a web search for the number of World War II soldiers killed rather than the requested answer-type label, and reaches an 8323-token rejection after 25 tool requests. Another child spends 17 tool turns on LangChain/package attempts. Root dispatch counts across its five tool actions are 2, 2, 6, 6 and 13.
- `fe197cde`: two actual root dispatch actions start 33 and 13 child invocations. Child work includes attempts to load a nonexistent names dataset and obtain dictionary definitions. The recorded traces do not establish successful network access or successful package acquisition.

## Why the executed runtime permits this

The pinned nano-rlm engine is commit `4ef3438d55fdd39b18d34035833c73e13b006733`, MIT. This is the executed Prime/nano path, not this repository’s `src/rlm`.

- `nano__engine.py:297–374` starts IPython and installs the built-in tool set at every admitted depth. At `:918–932`, depth controls the recursion wording, not Python availability. Its loop (`:380–550`) can make repeated tool/model turns. Actual configuration sets max depth 1 and per-provider response cap 2048; that response cap is not a one-call child limit. No compaction is configured.
- Actual child system messages start “You are a coding agent,” advertise persistent IPython, and suggest package installation. They omit the root’s `rlm` recursion instruction but retain the coding-role instruction. Root-generated child user requests explicitly ask for answer-type labels, so the irrelevant solver/package behavior is a model-policy response within a permissive role contract, not a requirement to execute code.
- Prime `RLMHarness` installs the pinned nano runtime, and the executed routing overlay only adds trusted attribution/role selection. It does not isolate children from tools. `max_depth=1` and the recorded trusted depths exclude nested model recursion as the cause here.
- Nano’s `call_with_retries` remains in the inherited runtime. It can wait 15/30/60/90/120 seconds on its enumerated transient failures; `BadRequestError`/HTTP 400 is not in that retry tuple. The 11 observed rejections are native HTTP 400 child requests with no sampled completion. The 648 distinct, attributed child model requests are not explained by that retry wrapper. This bounded projection does not measure otherwise unlogged HTTP retries or assign wall-clock delay to them; provider retry configuration alone is not proof that all outer transport waiting is absent.

## One smallest comparison to queue, not implement here

Test a **depth-1 role-clarity suffix only**, with the same root/child weights, native rendering, tools, sampling, limits and error handling. Proposed suffix: “For this child task, classify the answer type requested by each supplied question; do not answer the embedded questions. Work from the supplied text, without Python, package installation or external sources. Return only the requested labels in the requested format.” Leave the root prompt and child user payload unchanged. The control is the existing child coding-agent system prompt without this suffix.

Use four explicitly exposed development context/task groups (the three contexts represented above plus the existing 32-record training context), two fresh frozen seeds per context and arm: 16 episodes, paired by context/task/seed, interleaved on one fixed original-root/fixed-c32 child service. Warm single-A100 estimate 10–20 minutes, hard 20-minute budget with missing outcomes preserved. No training and no alteration to BROAD16 continuation admission. Since tools remain available, this tests policy sensitivity to child-role instructions, not enforced tool isolation; nonadherence is informative. A new wrapper would add the suffix only at the trusted depth-1 system-message seam and record original/forwarded message hashes and actual native prompt IDs. No code execution on the host, fallback, answer repair, forced recursion or oracle would be introduced.

Primary: paired exact root outcomes and total physical model calls/tokens per attempted episode, with four context-cluster summaries. Secondary: child invocations, calls per invocation, tool-request turns, observed tool errors, initial-versus-last child prompt lengths, unsampled context rejections, terminal schema/label validity and restart dispatch counts. A cost reduction with preserved/improved correctness would justify a larger test. Fewer calls solely because children become empty/invalid is not success. This is ordinary role specialization/context-management research, not a novel generic method or a causal result yet.

## Training blind spot and limitations

The frozen admission rules remove affected whole root trajectories when child physical calls are unsampled failures. All four raw outcomes were observable strict failures, but their root actions provide no gradient under that admission rule. In this run the unrecognized equal-8192 wording also stopped export before any update, so even the otherwise clean mixed rows were not trained. This can exclude exactly the costly root decisions that need improvement. The root-only correctness objective also has no explicit cost penalty. These observations do **not** authorize relabeling infrastructure errors, widening admission, discarding the frozen STOP, or claiming a valid policy-gradient estimator for partial traces. A future estimator/admission study would require its own declared causal-action and failure-observability contract.

## Evidence identities

All episode/source pointers are in `2026-09-09-child-call-amplification.json`, SHA `24959d53f484a3a08b90974aef77721fafd3a0769cc2d04595291cf67d604871`; read-only projection source SHA `040e3895cb4d851378661cf07beb893daf9b83fa44f288cf4141c69a834903b6`.

Sealed STOP audit: `../analyses/root-broad-curriculum-live-2026-09-09/REPORT.md`, SHA `9aedf22ed6397951f6e1f1a6bda67403af1c0bf8ef82a78477f1f2fbdd7b7991`; METRICS SHA `aa1825ad8ffba44e2800c8e95632950681117b4b77cba096552382ffe3484736`.

Pinned source paths under `/project/alex_phd/research-cache/2026-09-08-literature/`: `leaf-contract.7HPUr5/nano__engine.py` SHA `2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed`; `recursive-example.6xBrmx/src__rlm__client.py` SHA `883ed932ebc79770b17c986bf959e27c5bf786d4eeb5016ce8ce8f331a84cbee`. The recorded routing overlay produces engine SHA `841ca409ff888fc5b8de894ef46bc7e0089160067e5e6c704f45b15ce363b996`. Prime harness SHA `7256f1efe1d0b44c8488e62edc93c41fa2da1fae95620bc6de4dea2e7d517bfc`; `root-only-credit-v1/native_routing.py` SHA `5ea35866be87662372ca1b312ddabbbab9ce009915fbfaa31353455ec702e841`; `leaf-role-routing-v1/source/routing.py` SHA `8575081694a6ceea8d5f4058d4f625eb81d34f617a680f94bc06968e3a3ca78f`.
