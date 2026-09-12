---
question_id: musique-task-directed-followup-v1
status: CPU-prepared-exploratory-screen
dataset: official-MuSiQue-Ans-v1.0-train
selected_questions: 12
hop_distribution: {2: 4, 3: 4, 4: 4}
physical_calls: 132
terminal_slots: 48
arms: [stop, broad, targeted, full_source]
owner_seconds: 1700
science_seconds: 1320
external_seconds: 1800
optimizer_steps: 0
selection: outcome-blind-row-hash-rank-with-structural-exclusions
novelty_claim: false
GPU_authority: MAIN-only
---

Does a model-selected focused question elicit useful semantic information from an ordinary child report's original source that an equally costly broad follow-up does not? This isolates targeting from simply spending two additional report calls, and removes the observed Python-access failure without supplying gold decomposition or a host solver.

Each question has two balanced, label-blind paragraph halves. Two512-token ordinary reports and one256-token planner output are generated once and reused byte-for-byte by stop, broad and targeted terminal branches. All three final consumers have the same original question, reports and planning prefix. Stop answers immediately. Broad obtains two more512-token reports asking for omitted relevant information; targeted instead asks the planner's respective focused question, with the same halves and first reports. Each final has1024 tokens and the same answer/support schema. Full-source is an independent1024-token call over all original paragraphs, with no report/planner output. There is no forced lossy summary, Python, external retrieval or answer program.

Physical cost is11 calls/question,132 total: the common three calls are counted once in acquisition. Deployment-policy costs are4/6/6/1 calls for stop/broad/targeted/full-source, including shared prefix acquisition in each policy but not charging one policy for another. Paired broad/targeted follow-ups share seeds; all four finals share a seed within question. Different prefixes do not imply identical random outcomes. Four concurrent question workers use the same eager, no-LoRA, no-prefix-cache native service; branch order rotates by question index, independent of gold/results.

Primary is targeted versus broad; targeted versus stop establishes incremental information. Report exact answer EM, unchanged official answer F1 and support EM/F1, fixed12 C/W/U per arm, four questions per hop, paired12 outcomes, and full physical/policy input/output/observed wall costs with unknown usage separate. These are12 contextual units, not48 independent items. Known native length stops with malformed final JSON are model failures; unknown/native transport failures are unavailable. Invalid or empty initial reports/planning block dependent arms explicitly; the independent full-source control still runs. All132 planned stage IDs remain in the denominator, including start-only and unattempted records.

Prospective screen, not a significance claim: only a complete qualified panel may promote to a fresh replication. Require targeted at least3 net EM over stop and2 over broad, nondecreasing support-F1 sums against both, and at least3 stop-correct cases to establish potential stopping value. Report the full tradeoff regardless of screen. If full-source dominates cost and accuracy, retain that boundary and retire a deployment-gain interpretation. Failure does not establish that all targeted delegation is ineffective. No learned selector or second screen is implemented.

Fresh selected train records exclude normalized-question, exact decomposition-component IDs and supporting-paragraph content overlap with the previous12 and one another. Gold/decompositions remain host-only0600; original public question/paragraph text and indices are retained. Hash ranking and paragraph partition do not inspect model outcomes. This is a new local task-content panel, not unknown pretraining exposure, independent task operators, recursion necessity or architectural novelty.

The frozen source proposal remains unchanged. Its syntax sentence is corrected additively in PLAN: plain→syntax5→0 interface-usable and5→2 endpoint-correct, per the reauthenticated report. The completed depth pilot made112 root calls and no children/grandchildren, so it did not evaluate recursion's benefit. This fixed report graph tests a narrower semantic mechanism.

Runtime qualification is prospective explicit first real eager CUDA dispatch, not the optional Dynamo-warning marker that falsely withheld the released-base reference. Exact source/env/model/clean-release evidence remains required. A CPU sentinel is fixture evidence only; actual EngineCore PID, flag, enabled mode, original function return, source hash and shapes must be recorded in the admitted service. There is no bitwise invariance claim or mathematical kernel modification.
