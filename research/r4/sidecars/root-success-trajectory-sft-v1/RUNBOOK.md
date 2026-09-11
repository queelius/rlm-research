# MAIN launch and evidence

CPU preparation does not authorize a GPU launch. MAIN must authenticate READY.json and all listed source/input hashes, assign one empty GPU under the existing shared lock, and accept the exact command below. No new environment, server protocol or installation is needed.

```bash
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/project/alex_phd/envs/prime-rl-5990b1b/bin/python \
/project/alex_phd/runs/rlm-research-r4/sidecars/root-success-trajectory-sft-v1/launch.py run \
--output /project/alex_phd/runs/rlm-research-r4/sidecars/root-success-trajectory-sft-v1/outputs/attempt-001
```

Use the parent's4530s process envelope and120s exceptional owned cleanup policy. The wrapper uses one4380s work deadline/4500s inclusive envelope,1200s training child,900s per collection and the unchanged qualified service ownership/release helpers. It starts no concurrent services. Phase order is **RL7 → success-SFT8 → baselineefab**, fixed by SHA256(master:arm), after training. Startup/verification/release consume the shared deadline. No retry or cap reset. Separate CPU analysis runs after GPU release, not while retaining scheduling ownership.

Training uses `/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python`. Checkpoints are outputs/attempt-001/training/checkpoint-0001 through checkpoint-0008, each with state.json, adapter tensors/config, Adam and RNG. RESULT.json/SELECTION.json are written only for exact full8 completion. It is fresh efab Adam at pass0; a checkpoint retains its real continued optimizer. The original efab optimizer is never imported.

The learner consumes only prepared/EPISODES.json. Its27 teacher episodes contain114 exact physical root turns/15,256 targets, max2639 sequence tokens and168,412 total prompt-token exposures per pass. All114 physical completions already have the recorded151645 terminator; none was added. Eight full passes produce216 episode exposures/912 turns/122,048 target exposures and1,347,296 prompt-token exposures. These are logical training sequence exposures, not a claim of physical GPU cache hits or equal compute to RL. All recovery turns are retained. Weighted CE and token NLL differ and are recorded separately, with actual FP32 turn coefficients/masses in every checkpoint metric.

The source manifest includes candidate raw/native role/typed proof and the prior sealed screening decision. Startup authenticates closure once per process; native reconstruction ran once during CPU export and is not repeated per training turn or live episode. Child grammar likelihood is retained only as provenance and never receives root/SFT credit. No text is retokenized or generated code executed during preparation/training.

Readout raw rows, episodes, physical role/typed/wire evidence and TERMINAL.json live beneath outputs/attempt-001/{rl7,success_sft,baseline}/rollout. Each phase has an explicit binding, /models-authenticated actual descriptor, READOUT_BINDING.json and service release record. The24 frozen PLAN coordinates ×3 frozen phases define all72 planned cases. Keep any completed endpoint answer separate from episode runtime/trace cleanliness using raw fields; never recode a setup failure as a wrong model answer, or infer clean graph admission from the endpoint field alone. Incomplete/unstarted cases remain null; earlier completed cases remain observed after a later cap. No evaluation checkpoint selection occurs.

RL7 is adapter809fc46e…, fixed by exact original round7 COMMIT/state/input/correction/optimizer closure and STOPecd1c7f4…. It is last-saved after round8 lacked a mixed group, not an original final8 success. The baseline is efab2913…. New SFT final8 identity is authenticated from its actual RESULT/state/files before service starts. Both baseline contrasts are primary; SFT-versus-RL is an exploratory package comparison with unequal data/optimization budgets and a sequential-service nuisance.

CPU verification, without service/GPU calls:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 \
/project/alex_phd/envs/prime-rl-5990b1b/bin/python \
/project/alex_phd/runs/rlm-research-r4/sidecars/root-success-trajectory-sft-v1/launch.py verify
```

Checkpoint recovery is a separate MAIN-owned action, not an automatic rerun of the launch wrapper. Use the exact training interpreter and `train.py run --output <same training directory> --resume <its latest checkpoint-000N>`. Only a contiguous same-identity full-pass chain is accepted; data, source, initial root and step budget cannot change. Checkpoint state and completed invocation records preserve cumulative training time. If a process was abruptly killed without its invocation timing closure, automatic recovery refuses rather than invent spent time; MAIN must resolve that provenance boundary before any new recovery design. A failed partial gradient pass is never committed. After exact final8 recovery, MAIN may explicitly schedule the same frozen readout; no recovery path silently launches a service.

Focused tests are CPU-only. The tiny in-memory PEFT save emits its known missing-base-config warning, disclosed in CPU_TESTS.json; it does not indicate missing production adapter tensors. Full rootless/native/provider qualification is inherited unchanged and authenticated; the stronger current-data check reconstructs all114 actual teacher root calls from native graphs and wire records. No fixture likelihood enters training.
