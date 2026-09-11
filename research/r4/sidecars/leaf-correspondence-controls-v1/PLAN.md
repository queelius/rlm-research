# Leaf Correspondence Controls Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline for this parent-approved sidecar.

**Goal:** Queue24 representation and32 rotation calls without live model contact.

**Architecture:** Privately load the frozen fixed-leaf collector and replace local request/scoring callbacks only. One new driver owns validation slicing, strict parsing, immutable endpoint binding and summaries. Existing files remain read-only.

**Tech Stack:** Existing Python3.12,httpx,tokenizers/transformers,vLLM0.28 protocol,XGrammar0.2.1 CPU.

**Spec:** DESIGN.md and parent approval confirming validation720 order.

This checklist is a frozen implementation input, not a mutable progress log. CPU_QUALIFICATION.json and the last-written READY.json provide the actual execution/completion evidence.

## Global Constraints

Old c32de only; first256/300 validation records; seeds981261401/402;24+32 calls; fourworkers;300-second caps; no GPU launches. Native system/definitions/tools retained. Strict IDs; free echo strings. Authorized isolation is this external sidecar, not a new Git branch.

### Task1: Data, requests, parser

Create driver.py/test_driver.py. Interfaces: build_spec(comparison),make_request(design,row),score_response(content,scoring_context).

- [ ] Write literal four-item rotation, duplicate/missing-ID, copy-fidelity and inherited-request tests.
- [ ] Run pytest and observe driver-missing assertions fail.
- [ ] Implement layouts, exact treatments and strict parser; run focused tests.

Required literal: rotated location/numeric/human/entity under order2,3,0,1 returns source human/entity/location/numeric. Wrong copied question plus correct label keeps label-correct and marks copy_exact=false.

### Task2: Binding, collector, capture

Interfaces: bind_spec(frozen_path,endpoint_path),collect_calls(client,url,spec,output),score_coordinate(design,coordinate,records),run(bound_path,output).

- [ ] Test actual inherited dispatch using only a network fake; retain malformed outputs with no retries.
- [ ] Test rejection of non-c32de weights and wrong live alias root/base.
- [ ] Implement private callback reuse, source-order item metrics and capped runner. Checkpoint every call including null infrastructure errors.

### Task3: Freeze and queue

Interfaces: qualify(spec); CLI design/preflight/bind/run; README with supplied actual endpoint.

- [ ] Validate all vLLM request objects; compile distinct grammars; verify free copy strings and rendered length budgets.
- [ ] Freeze selected inputs, source hashes and two unbound specs; publish CPU_QUALIFICATION.json.
- [ ] Fresh focused tests/preflight, then READY last. Inline CPU preparation already approved; no execution-choice question.
