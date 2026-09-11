# Receipt ablation: bounded independent source review

Reviewed 2026-09-09 06:31–06:36 UTC against the final published READY and all three decision documents. CPU/read-only review; no tests rerun, generated-code execution, container/service/model/GPU calls, signals, acceptance or frozen-file edits. This is not launch approval.

Verdict: no Critical/Important mismatch found in the primary 72-episode allocation, fixed-weight binding, rootless helper/broker integration, gold isolation, or exact-score comparison. Two concrete limitations below require explicit interpretation; the inherited lifecycle race remains an operational risk, not a model-quality result.

## Checked evidence

- Authenticated the union of SPEC source and READY artifact closures: **224 distinct paths, zero hash mismatches**. Read all ten new Python files and RUNBOOK, then the necessary inherited collector, task setup, native routing, broker and lifecycle seams. Direct JSON checks independently reproduced 72 unique coordinates, 24 matched triples/seeds, 12 tasks and six contexts. All six serial within-worker arm orders occur four times. The actual collector adapter changes exactly the two queue-chunk literals 2→3; its worker iterates every row in a chunk. Eight workers therefore dispatch eight coordinate triples, not split/mispaired two-arm groups.
- Fixed root is historical step8 `473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd`; child is `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`. Binding/descriptor checks preserve exact adapter/config/base identities and the inherited live `/models` alias/path/parent check. Trusted depth headers select root versus child; native wire hooks require Qwen3 thinking rendering, T .5, top_p 1, top_k −1, min_p 0 and max_tokens 2048. No new model client or broker transport is substituted.
- `ReceiptTask.setup` calls inherited setup, which writes only `context.txt`, then writes the local module, public catalog and arm config. Independently checked all six catalogs: exactly 64 records each, positional IDs, public field whitelist, record byte hashes and reconstructed context hashes match. No gold answers or labels are copied to these files. Host gold remains in the inherited task/scoring object, outside the model payload. The unchanged arm retains the historical task class/prompt and only the context file.
- `rlm_records` calls the existing active-scope `rlm.api.run` once; `RawView` preserves the original RLMResult/answer/session/usage/turns. Receipt derivation occurs locally after the broker’s exact four-field response has returned. The current parser requests and validates a **source-ID→label JSON object**, not the superseded array: duplicate keys, missing/extra IDs, wrong value types/vocabulary, non-JSON constants and extra prose fail without repair. Invalid mappings remain null, raw text and returned key order survive, and validity does not certify semantic labels. Unknown/duplicate requested IDs fail before a model call; broker errors propagate.
- Current `qualification-map-attempt-001` evidence—not the preserved superseded array fixture—contains three real pinned rootless/native CPU episodes, each root→child→root, nine fake-provider calls and zero actual model/GPU calls. Independently checked all nine retained role results: exact bound aliases, depths 0/1/0, returned HTTP 200 and T .5. All three installed-engine overlay records bind original `2e04fe…` to the qualified overlay. Indexed-raw and receipt fixture child requests have **identical 688-token physical prompts**. Both helper arms demonstrate the original four-field broker round trip. These fixed token/logprob fixtures establish the seam, not model competence or likelihood agreement. The recorded focused-test artifact reports seven passing tests; I did not rerun them.
- Primary contrast is receipt minus indexed-raw. Both use the same helper request constructor; only optional receipt access/minimal documentation differ. Prompt-only token counts are 566 unchanged, 314 indexed-raw, 349 receipt. Removing the old procedure/example in both new arms makes comparisons to unchanged a practical harness-package comparison, as disclosed—not an isolated indexing treatment. Identical helper arguments imply identical requests; actual root-selected calls need not remain paired.
- `results.summarize` preserves unknown outcomes and unrun coordinates, checks duplicate/drifting coordinates, and computes only observable matched contrasts with six context summaries. Strict task scoring is inherited, not replaced by receipt validity, coverage, shape or helper uptake. Recorded runtime failure, budget cancellation, >50% execution-error early stop after eight rows and missing traces remain distinguishable. Collection uses 2100 s, work 2280 s, owned envelope 2400 s and requested outer cap 2430 s. The new driver does not run its expensive terminal analysis before exiting/releasing scheduling authority.

## Limits and actionable cautions

1. **Source-bound by normal helper execution, not tamper-proof evidence.** The module/catalog/audit are runtime-local and root-writable. `results.py` preserves helper evidence and verifies native episode capture, but does not independently match every helper event’s selected source bytes/request hash to its actual native child request. Therefore helper logs/access counts alone cannot establish verified coverage or actual use in the final aggregate. Corroborate any such claim from frozen host-public catalogs and physical calls; retain missingness if not observable. The raw arm also has the module on disk, so this is an offered/documented interface contrast, not adversarial prevention of parser access. None of this changes host exact-score comparisons.
2. **Known lifecycle race is still inherited.** New `driver.py` imports the old factorial coordinator/lifecycle and calls `life.install`; it does not import the later continuation process-observation shim. `campaign_lifecycle_v2.observe` calls `campaign.process_identity`, whose `/proc` reads/`os.getpgid` can raise FileNotFoundError/ProcessLookupError if an observed descendant exits. This is the same class of launcher race that stopped the independent-seed run. Existing startup failure cleanup is retained, but launch/release failure must be classified operationally. Any remedy must be additive and newly bound; this review did not alter or accept one.
3. **Secondary projections are narrower than the raw evidence.** Inherited AST markers can aggregate unparsed cells as zero; retain `unparsed_root_cells`, never interpret that zero as absence. Physical cached-token totals are currently explicit null despite potentially recoverable wire usage. Native attempt counts have missing-count diagnostics; summed overlapping call durations are not elapsed GPU time. Helper audit read failures are not proof of non-use. Nano’s internal retry/delay caveat and possible partial-trace loss remain explicitly frozen in SPEC; no new retry is added.

These are six already exposed, leaf-training-supported TREC contexts and 24 repeated coordinate triples, not 72 independent problems, novel-task confirmation, a proof of semantic correctness from syntactic receipts, or evidence about the ongoing independent-seed outcomes (not read).

## Bound identities

All paths below are relative to `sidecars/root-receipt-ablation-v1/` unless noted.

| Artifact | SHA256 |
|---|---|
| READY.json | `1eba49031384deda22bbfdd9d234cc7ff1b43e63c0b72081af2c7c270a5b74f2` |
| SPEC.json | `90000411c23cc92ad1ed21906cd30a5687bfa315e509b19eecc9e3792532b198` |
| driver.py | `e3b936b3d2a5358fe4682cad0a875a28673bb7aae7fe06de4606567fee5ff32e` |
| experiment.py | `1803aa59cfaf94edf7ac5db865cce4c721eb2302b31ab186c5b88b0fc4488690` |
| receipt_api.py | `4ffaccc9ad15ee088ab1f6d50545a8d9bf269cf2481febaf5bf5d42e333706a6` |
| results.py | `4878bf245d105a41e7d008343f8bbaae577832c800cff11964222276c02d012a` |
| qualification-map-attempt-001/RESULT.json | `e358ecdfb36b6af9f2c1b985061677c9b9d67647676f459136b0e4e4f5ad2fbd` |
| inputs/PLAN.json | `524bdb9f2a76d5bb8a8d3e882ca380e7c5dcd4a01392dd07369b3bf2dcb5ad1c` |
| inputs/TASKS.json | `79b7e68eb40a229f5f9876f89ec72f6bc616ea3a1775c9ed3cfb57c3a5974389` |
| inputs/PUBLIC_CATALOGS.json | `4acd48b819a24e6bce2b8366a04c1b763614e250113b33fa32e6f6af2ec252b8` |
| inputs/BINDING.json | `4fb1e1a16ff278a4d0bf1d935ccf48fced843e84861592e4ae4f2031d53d08e2` |
| DESIGN_PROPOSAL.md (beside this review) | `b4d8eb855d790744675b2efe7f05f44dab364e6138f5d5b37ca1b731c48c69cf` |
| RECEIPT_IMPLEMENTATION_DECISION.md (beside this review) | `41ebbdfa9ee058e0e2857e579f0519c9964833818830f94add08080497c16d4f` |
| RECEIPT_FORMAT_AMENDMENT.md (beside this review) | `cfda51512eb467317995f0e2e65458078e3efb1881132e33100ca0266ed556ad` |

Full remaining source/test/qualification identities are authenticated by SPEC/READY. No global authentication was repeated per episode. Read-only checks here used saved deterministic qualification fixtures, never live study outputs.
