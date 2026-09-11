# Warm V3 first-commit CPU verification

No actual commit or lifecycle defect found. This is author-assisted verification: runtime_port authored V3, and MAIN/question_cards provide independent review.

Checkpoint1 state SHA `ce5a945fa3fac95a5f8924b620190745207dbc6c470a6da83ff4bd7352b5a3a3` and allfive saved payload hashes match. CPU-safe loads verify504 finite FP32 Adam parameter states at step1, lr5e-5, weight decay0; Python, CPU and one CUDA RNG tensor are present. All504 adapter tensors are finite and root-LoRA-only; independently computed delta0.200715756166352 matches the trainer's0.200715756166096. No model/base load or GPU work was performed.

Original immutable24 export independently rebuilds the13 mixed selected episodes. All76 current-root-action masks,5173 action tokens, zero child/observation credit, native rollout logprobs, TIS ratios/capped weights, per-turn loss and equal episode→turn weighting agree. Distribution-summary arithmetic and guards agree; the87.656425-second optimization duration is a trainer receipt, not independently retimed.

Exact TRAIN_COMMAND points to original attempt002 GROUP/GENERATION and new attempt003 training output, GPU visible=true. No duplicated window1 collection or prior original training exists; source hashes match. At09:43 UTC checkpoint2 also existed, with previous optimizer/RNG/state hashes matching checkpoint1; window3 generation binds step2. Window2 service release was verified before its trainer start. No readout directory was present at the check.

Detailed receipt: `analyses/root-sft24-terminal-rlvr-live-2026-09-10/V3_CHECKPOINT1_REVIEW.json`, SHA `95b6d2d78bdc8eeda9b48f3ed808bc44c8b6079702264101ba1036ae238db6d1`. Source script SHA `3df6fd7f44519ab976daa8c2467b4c689186b09d38e693b6feb8533d51c9f2e3`. Prospective staged-read protocol is `V3_STAGED_READ_PROTOCOL.md` in the same analysis namespace; original METHOD/V3_BINDING metrics and first/last paired96 are unchanged.

Actual parent COMMAND start1789032640.0602996, SHA `6efb51a7ad898315a85c75c6f1654a5b86d5dc1436228ab235467f01ab1c4979`,10419-second cap. Current outcomes do not authorize changes to training, checkpoint selection, frozen inputs, services or the live queue.
