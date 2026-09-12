# AG native/HF one-step: CPU readiness

Sealed on2026-09-12 at approximately11:44 UTC, after approximately19 minutes of
bounded CPU implementation. No GPU launch, installation, prior-source modification
or changes to queued collectors. This is readiness evidence, not a training result.

Source directory:
`/project/alex_phd/runs/rlm-research-r4/sidecars/helper-agnews-native-hf-onestep-v1`.

Training READY SHA
`9fa4df0e9921f35202abe0627914eda17be2851e089f7402c5f37d0830616be6`, identity
`2577eaf314affca726c8a680d5740d88461c2f2bff2459fdf9c6c644d81c8e46`,337 closure pins.
Conditional EVAL_READY SHA
`d3caf49d6b4fa320c4e8116e33230f409b7077472156568531600049d6ca846b`, identity
`2231a179b567c92fa326039e9c1d35abfc4b5f4d2178e453dabe9d63c5a52182`.
Full source inventory, environment versions, QUESTION.yaml/MD and exact input
requests are included in the closure. Existing READY_C32_V2 remains untouched.

Native four-key token/gold/mask/runtime/dependency/evaluator fixture passed8.60s.
Tiny HF/PEFT fixture over128 toy actions passed8.21s: an actual update, an importance
gate failure, and an actual gradient replay mismatch with no weight change.
Known native XGrammar SWIG deprecation warnings are preserved, not hidden.
CPU_TESTS SHA `f6dcaafa9f33ac6848be7690ea3634f886f8f65e2b1aeb1d8a35db90b4d8498a`.
Fresh post-seal owner verify, eval-owner verify and Ruff check all exited0.

MAIN-only training command, under shared GPU lock and external1200-second timeout:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/helper-agnews-native-hf-onestep-v1/owner.py run --outer-seconds 1100
```

Native128=32 B4 groups x4 actions, T.5, count RLOO/128; exact original importance
and replay gates; original c32, fresh AdamW, one update. Native650/CPU-mask60/HF350
phase ceilings fit within the bounded owner; no step on partial/invalid inputs or
gate failure. One native service then complete release, native-CPU masks then one
HF model load. The maximum1133-token prompt plus1024 completion cap is2157 versus
the actual service cap8192, checked again before collection.

Conditional updated AG256 readout, external700 seconds:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/helper-agnews-native-hf-onestep-v1/eval_owner.py run --outer-seconds 600
```

This waits on no data implicitly: MAIN may invoke only after UPDATED. Full
qualification, source/state/optimizer/checkpoint hashes and child-only binding are
checked again. It reuses the exact existing64-call V2 AG-only evaluator with the
same256 heldout records, B4 schemas, temperature0 and fixed seeds. Baseline source
reuse still requires matching actual runtime and complete raw qualification.

Limitations: the numerical fixture is CPU/tiny-model evidence, not a claim that
the real GPU replay will pass or the model will improve. This bundles new data,
domain, request size, reward and dose. The frozen heldout256 is excluded from
training but research-exposed after existing readouts; base pretraining is unknown.
Every result, including NO_UPDATE, remains an exploratory package readout.
