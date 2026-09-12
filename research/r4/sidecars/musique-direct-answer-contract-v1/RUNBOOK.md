# Direct final-answer contract, all12 exposed MuSiQue cases

Question: can clearer answer-phrase wording recover the observed exact-answer surface failures without an extra helper? This is one adaptively proposed instruction intervention on all12 exposed cases, not new information, learned routing or a demonstrated improvement in composition.

Use the exact cached MuSiQue Qwen3-4B-Instruct-2507 base checkpoint and qualified V3 service, not procedural-SFT cp32 and not a research adapter. All12 frozen flexible-four paragraph payloads, original questions, system messages, final JSON schema, support_idxs, T.5, max1024 and final seeds202609230003+16i are unchanged. Append only the same universal instruction in study.ANSWER_RULE to the original final instruction. No examples, per-question patches, teacher components, gold, cached answers, helper reports, new selectors/planners or fallbacks enter inference. Source payloads remain exactly the qualified original cached direct payloads.

The new instruction asks for a shortest standalone answer phrase, preserving quantity qualifiers and units when the question asks for a measurement; no explanatory sentence, changed entity, invented bridge or external information. It explicitly retains concise lack-of-evidence behavior and the support_idxs obligation. Old and new prompt tokens intentionally differ only through that appended instruction; preparation saves the exact expected new native requests for all12 and authenticates equality of every other request field. This does not assume a model will follow the instruction or normalize a generated answer afterward.

Cached direct12 scores remain frozen at3/12. All answer/support metrics and raw native completions are retained. Known malformed answer JSON is an available model error with the existing zero score; native failures are unavailable, never silently converted to wrong answers. All12 remain in denominators/pairing; no retry, replacement or best-output selection. Source/answer-format/faithful-joining distinctions require a separate inert outcome audit.

Physical new work:12 calls and12 finals. Cached acquisition36 and direct12 calls are separately inventoried. Natural full policies both4 calls/question (48 per arm), conditional finalization1 versus1; token costs are not matched. The previous quoted-relations5/12 result is context only, not this experiment’s direct control. No primary result is rewritten.

Four question workers. Science700, owner950, external1050 seconds; actual prefix plus requested output≤8192. Same authenticated V3 request/response decoding, actual dispatch/lifecycle/release, immutable native request/response/prompt/call/question receipts. No generated code execution. Preparation and focused HTTP-double fixtures are CPU only and do not start the service.

MAIN alone launches after source/READY review. Verify CPU readiness:

```bash
CUDA_VISIBLE_DEVICES='' /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/musique-direct-answer-contract-v1/owner.py verify
```

The sealed READY supplies the run command for MAIN’s capped queued owner. Do not run that command during CPU preparation.

Active CPU evidence is CPU_TESTS_V2.json and cpu-fixture-002. The initial fixture receipt is preserved: its failure was a test comparing a token list to the tokenizer's mapping return, not a runtime model call. A separate red→green regression covers the real pre-seal JSON key-order issue; the new prompt is now checked against every cached prompt byte-for-byte except the appended instruction.
