# Candidate1 feasibility: all-fresh-root state-representation/restart pilot

2026-09-09. Design only, awaiting MAIN review; no implementation, GPU, service, lock or active-source change. This memo follows MAIN's explicit preference for all-fresh roots over a new historical-graph import seam. It is **not exact native-history continuation**. Existing unchanged controlled continuation is a separately labeled reference, not the causal baseline.

## Recommendation and useful question

Feasible with the existing native task/setup/provider machinery:16 actual pre-correction source states ×3 fresh-root representations =48 new endpoints, unchanged low66c root and fixed c32 child, proposed2400s outer envelope. Does a faithfully exported artifact state preserve actual evidence use and strict-answer accuracy relative to putting the genuine transcript directly into a fresh root's context, at lower paid continuation cost? This tests restart packaging/retrieval, not learned summarization, long-context memory, adaptive decomposition or equality to a live uninterrupted agent.

Three paired conditions, all with fresh REPLs and identical authorized evidence files:

| Arm | New root's user prompt |
|---|---|
| Q: quoted history | Common original goal/instructions and artifact index, plus verbatim root-visible pre-correction messages explicitly quoted as historical data |
| A: artifact references | Same common goal/instructions and index; maps/history accessed from the common files |
| M: metadata inline | A plus deterministic public metadata: source IDs, batch coverage IDs, file locations, original requested users/target, and that reduction/finalization remain unresolved |

The metadata file itself is common to all arms; M changes inline salience, not authorized information. Retain original actual predictions, including wrong labels. Do not provide an answer, category totals, selected answer-bearing records, repaired labels, new classifications or privileged gold. Prefer unmerged ordered map pieces, each tied to its actual observation/source ID; any derived coverage is purely ID membership, never semantic scoring. No target-specific summarizer.

## What exists, and what the honest cut excludes

All16 CONTROLLED_PLAN source directories contain TEACHER.json and EPISODE.json:4 contexts ×2 query compositions (`u02`, union `u00,u02`) ×2 batch widths. Eight width16 states use `categories`; eight width4 states repeatedly overwrite `labels`. There are40 actual historical child acquisitions. No controlled heldout state has the intentional metadata error. Native pre-correction prefixes are1389–1406 tokens for width16 and1736–1753 for width4: useful state-use variation, but not a long-history stress test.

The cut is exactly `turns.corrective.input_ids[:prompt_length]`, corroborated against the ancestral root-visible graph ending after the final producer observation. Export only original system/user text, authored producer actions and their actual returned tool observations. Do not export private child graph messages merely because EPISODE contains them. Source producer actions are authored, child predictions are actual; report that distinction.

TEACHER contains future authored corrective code, a computed scalar and terminal answer; EPISODE continues through them. **Neither whole file may be mounted or copied wholesale.** Exclude corrective/terminal actions, observations, target labels/masks, scalar, final, host gold, later sampled readout traces and evaluation feedback. Derive the package from the cut's actual observations, and compare its map pieces with TEACHER.visible_maps only as a private provenance check. Bridge_audit owns qualification of the current controlled readout; this memo is a structural feasibility pass, not its replacement.

## State-equality contract and minimal seams

Start every endpoint in a new native runtime/session/REPL. Never replay producers into Q alone or recover an old kernel. Width4's live `labels` holds only the final four records, whereas its history contains all16; other latent objects include `child`, `batch`, imports, IPython `_ih`/`_oh` and session logs. Canonical fresh state removes those asymmetries. No pickle/checkpoint of Python objects is needed or appropriate.

Write common byte-identical `records.json`, `context.txt`, original-goal `query.txt`, qualified `batch_contract.py`, ordered map-piece files, a metadata manifest and the sanitized pre-correction transcript archive into all three runtimes. No `count`, merged target scalar, corrective helper, old history globals or prior-session log. The full transcript archive remains available in A/M: their roots may choose to retrieve it, and its retrieval/tool/model cost counts. Thus the estimand is inline context versus on-demand evidence, not withholding the source history.

Material setup detail: AdaptiveTask.setup writes `query.txt` from `plain_query`, and native.task currently sets `plain_query=prompt`. If arm-specific prompts are passed unchanged, the on-disk query files would differ and Q's history would leak through an unintended second path. A new task subclass must separate arm-specific `data.prompt` from common original-goal `plain_query`, then write identical artifact files in setup. Ordinary new-session logs necessarily reflect the arm's declared prompt/tool actions; this is the intended representation difference, not imported old state. Do not expose different old `$RLM_SESSION_DIR/messages.jsonl` histories.

The normal ACP entry accepts user messages only; there is no qualified arbitrary native assistant/tool-history import at that seam. All-fresh Q therefore quotes historical messages inside the actual new user input. Its real graph and actual native prompt tokens honestly represent that quoted text. Do not substitute a historical token prefix behind a different recorded graph or claim Q is the old native role sequence. No engine/history-import change is needed for the recommended design.

## Pairing, scoring and modest budget

Use all16 source states, not those with successful downstream answers. Freeze a fresh seed per source shared by its3 arms, balanced/rotating arm order (16 gives5/5/6 per position), and the exact source cut/file/native prompt hashes before launch. Same unchanged low66c adapter, c32 child, tools and common accurate-field instructions; T0.5/top_p1.0/native per-call2048 cap,8192 context cap and180s per-endpoint wall cap, matching qualified machinery. All actual paid roots are free to inspect files, compute, call children or answer. Count actual file-map use, executed scoped reduction and reclassification, not filename/AST presence or scalar agreement alone.

Retain48 planned coordinates, strict whole-strip `Answer: N`, dataset correctness and actual-source-map consistency separately. Missing/failed/unreturned/unverified endpoints are NULL; authenticated malformed/capped final is observed0 unless it satisfies the strict contract. Never impute a missing endpoint as0. Report within-source paired differences, width-specific results,4 context clusters and8 query compositions; these source contexts are already exposed, not fresh independent validation examples.

Proposed wall allocation: up to300s lifecycle/startup,1800s collection (4 workers),180s release,120s margin =2400s. First CPU objective is package/prefix fidelity and actual prompt lengths, not outcomes; confirm every arm fits the native context cap without truncation. No new acquisition required. Qualified native final/branch checks, one package no-future-leak regression and one byte-equal-file/new-prompt namespace fixture are sufficient before READY; avoid a broad runtime refactor.

Historical40 child calls cost37340 input/2430 output tokens and28.243s summed physical child time. Full16 source capture job slices sum280.985s, which also include runtime setup, authored correction/final transport and teardown—do not mislabel all of that as minimal state-creation cost. Preserve it as observed gross provenance; derive pre-cut elapsed separately from actual event times if available, otherwise mark unknown rather than subtracting a guessed overhead. Charge each hypothetical endpoint its complete relevant historical acquisition: across48,120 hypothetical child calls/112020 input/7290 output, versus40 unique historical physical acquisitions already paid. New export/reconstruction CPU time, runtime/setup, file reads, new model input/output/cache usage and elapsed time are additional and recorded. A/M may save prompt tokens yet lose wall time to retrieval; no guaranteed savings.

## Decision before implementation

Rank this all-fresh48 pilot first. Promote if A or M retains evidence-use/accuracy with less total continuation cost on both widths; if Q helps, inspect whether it supplies useful action examples rather than superior facts. If all are near ceiling, use deterministic packaging as the baseline and seek longer/disjoint interruption states before training summaries. Keep exact native-history restoration deferred: it needs new graph/state semantics and is unnecessary for this question. Current unchanged controlled results can contextualize restart loss, but different seeds, live variables and histories prevent a causal subtraction.

Inspected source pins: corrective collect.py `b0c760dec08d3cb54db297da4daf89c47eef42592d0a9c9d4e50f2d6ab497443`; protocol.py `21f1789587e60ac49e3443c375db7c08afef622a75d7457531f6c9b3d6ddc6a1`; study.py `5e509fcc7285acb443b43f81491377eb76dbfd58e5d194e9c676a641a16246de`; CONTROLLED_PLAN `6f91b09e954570e314d06a7b69c2eb24d9e901010f9e906d85acb572ad6d1de0`; PROMPTS_ACCURATE `09fd0e7fad7fb79d929214cd71dd089d0e7a60919cf93c3f2f4f6dfb4558cca7`. Base path: `/project/alex_phd/runs/rlm-research-r4/sidecars/root-corrective-reduction-sft-v1`. Also read native.task, AdaptiveTask.setup, and ACP user-only entry. Full source/output freeze remains a prospective implementation step after MAIN approval, not READY now.
