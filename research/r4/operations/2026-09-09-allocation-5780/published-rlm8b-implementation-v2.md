# Published8B additive accounting V2 — CPU ready for re-review

READY_v2 SHA `5815d3583cddb82060343ed5d5427044df06ce129002cd1b026fdf0dcc2c8924`; identity `e282cf84f7b7eef9fdf6c4dd57967a775831fb12b2b161a1e89edc12b3087511`. Actual qualified-native `owner_v2.py verify` exited0 after1,373 pins, including the full original model/source closure. No GPU/model service or scientific attempt launched. Bridge received the source paths for independent re-review.

Exact launch argv, MAIN authority only:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-published-rlm8b-reference-v1/owner_v2.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-published-rlm8b-reference-v1/outputs/attempt-001
```

The new owner dispatches `collect_v2.py`; all old sources/READY/scientific inputs remain unchanged. Original owner SHA `f1f11bcea6b707f81379493e2e227458df7d8c177261372648fbe186fc4c4741`, collector SHA `95c8e4b2f1810516ea8b0652628f86f600df70a0a479a9f39b380a67b5475b3d`, READY SHA `be084ff6109ed23ab4e78c0236382aadda9a89f1a15073e1350c97de04824b2f` were freshly rechecked after qualification.

Two approved corrections only:

- Every endpoint's physical ledger is reconciled with on-disk calls, including late calls omitted from existing episode RESULT. Role/index/path identities deduplicate embedded and on-disk records; unmatched known calls and unknown requests remain. Original endpoint score/terminal/outstanding state is preserved exactly, not salvaged.
- Native final authentication follows historical execution precedence: current-iteration actual block final, then standalone FINAL_VAR retrieval, then literal FINAL. Matching raw native root/current iteration/terminal and zero outstanding calls remain required. Prior-iteration observations cannot promote a final.

15 narrow old+new tests passed11.43s (`CPU_TESTS_V2_002.xml`). A real isolated native root→child→stored answer→next-action in-block FINAL_VAR fixture reproduces V1 falseNULL and V2 availability. Other tests preserve native mismatchNULL, duplicate-ledger identity, late response usage/unknown requests, no score salvage, stale-observation rejection, exact V2 collector argv, and original composed service/GPU-environment behavior. The initial fixture incorrectly expected fresh variables to be visible inside the same historical execution; its failed receipt/artifacts remain preserved. No historical source was modified. No `rv8b-` qualification containers remained in the final read-only inventory; unrelated active containers were untouched.

Detailed immutable [AMENDMENT_V2.md](../../sidecars/root-published-rlm8b-reference-v1/AMENDMENT_V2.md) SHA `7c0e86ec21d95e48207e682f3d023dc34fad4c871dc35951dacf8bb2f31fd9bc`. Original3600/3330/3480 envelope, tasks, seeds, order, weights, paper reconstruction, service, isolation, cleanup, and unused attempt-001 namespace remain fixed. No broad infrastructure or scientific redesign.
