# Counterfactual-card96 Implementation Plan

> Use executing-plans inline, scoped TDD and external namespace. MAIN is reviewer/launcher; no subagents, Git integration, broad suites or environment mutations.

**Goal:** executable96 endpoint fixed24/c32 readout using exact selected GATE and card.
**Architecture:** narrow ph48 lifecycle/collector reuse; new pure variable-threshold oracle and deterministic input preparation. Scientific sources never edited.
**Spec:** DESIGN.md and ideas/2026-09-10-counterfactual-card96-addendum.{md,yaml}.

- [ ] Task1: `test_task.py` tests original/selected question and variable-threshold oracle, privategold invariance, exactcollectorCLI. Run RED; add `cf_problem.py`, `cf_study.py`, `cf_collect.py`. `answer(records,labels,row)` must use `row['threshold']`, not inherited5. `make_task(context,row,gold)` changes only P prompt card.
- [ ] Task2: `test_inputs.py` demands all96/24blocks/8parents/4cells, matchingcardpairs and source originals, selected GATE rows, no extra taskfiles/oracle, exact repeatedseeds and balancedorder. Run RED then `prepare.py`: freeze16 publiccontextvariants/48rowtruths/96prefixes, copiesof GATE/card, exactsource/seedpins; do not rerank. Countertext uses canonical JSON-lines of changedrecords. `FREE_PLAN`, `EVALUATION_PLAN`, `PAIRS`, `HOST_GOLD`, `PUBLIC`, `PROMPTS_ACCURATE`, `PROVENANCE`, `BASELINES` all written once.
- [ ] Task3: `test_owner.py` exercises actualowner→servicewrapper→interceptedPopen plus terminationrelease/96NULLinventory/rawcost including missingRESULT. Reuse qualified `cf_owner.py` with96stop and3600/3450/3570 clocks only. Preserve120release and rawphysicalunion.
- [ ] Task4: `test_native.py` exercises all4cells actualnative firstprefix2048, one child request with exact realIDs, actual observedmap and grouped reduction, authenticatedfinal; child labels authoredfixture only, gold still source-derived. Run focused CPU tests via qualified Python, no live model/service.
- [ ] Task5: `seal.py` runs only focused newtests, pins active accepted ancestorclosure, exactGATE/card/inventories/allinputs plusqualificationreceipts; writes READY with exactrun/verify argv. Run actual `cf_owner.py verify`, publish O handoff and exacthashes to MAIN. No source changes afterREADY.

Test command: `/project/alex_phd/envs/prime-rl-5990b1b/bin/python -m pytest -q test_task.py test_inputs.py test_native.py test_owner.py`.
Owner entry: samePython `cf_owner.py run --output <this-sidecar>/outputs/attempt-001`; verify: samePython `cf_owner.py verify`. This agent runs verify/CPUfixtures only.
