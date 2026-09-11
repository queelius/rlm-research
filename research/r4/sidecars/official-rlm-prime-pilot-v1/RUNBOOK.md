# Official-OOLONG / Prime-RL pilot

This sidecar is GPU-ready, but it is deliberately an adaptation rather than an exact
reproduction. It asks a narrow question: can a 4B model receive an OOLONG answer reward,
learn through a real LoRA/GRPO update while using an RLM-style Python harness, and improve on
questions drawn from a held-out context?

## What is pinned

- Official RLM: `854e688fbba9d8f8989e3da9989812e4b6dfe270` (read-only).
- Prime-RL: `5990b1b9bad63bf78640f45175e02eea04dbb30f` (read-only).
- Model: `Qwen/Qwen3-4B-Instruct-2507` at
  `cdbee75f17c01a7cc42f958dc650907174af0554`, Apache-2.0. The config uses the fully local
  snapshot at `/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554`.
- Dataset: `oolongbench/oolong-synth`, `validation`, commit
  `f0d59eaf0febf130664cfceb710436c8e3216b2b`. The selected source parquet and every row are
  hashed in `data/selection.json`. `data/tasks.jsonl` is a sealed local copy with SHA-256
  `4a071f628a2d028b6b9ae53660b53bf4cc39e47a4bf49ab758fa41c4a3034b6d`.
- Prime environment: `/project/alex_phd/envs/prime-rl-5990b1b` with Python 3.12.12,
  Prime-RL 0.9.0, verifiers 0.3.2.dev36, torch 2.13.0+cu130, and vLLM 0.28.0.
- Prime's nano-RLM ref: `4ef3438d55fdd39b18d34035833c73e13b006733`. The built-in
  harness cache is pinned at
  `/tmp/vf-rlm-4fa91253816bfa64435b7b727ec01bac2a7a7a2b72ece29ceb2474d26f95418d`.

The sealed slice has 16 training tasks from OOLONG context window 8 and eight evaluation tasks
from disjoint context window 6. Both use `trec_coarse` at nominal context length 4096. The model
prompt contains the question and a path, while the roughly 10,000-character context is written to
`context.txt`; the root model is not handed the context inline. The slice mixes label, comparison,
numeric, and user-frequency questions. It is a candidate calibration slice, not yet known to land
in the desired 20–80% base exact-success range; the initial smoke evaluation measures that.

## Important compatibility result

The pinned official training code cannot run unchanged on the pinned Prime stack. Official
`rlm_train` and `oolong` import the removed verifiers-v0 module `verifiers.types`; Prime uses the
v1 `Taskset`/`Harness` API exclusively. `artifacts/compatibility-probe.json` records the exact
imports and errors.

The adaptation keeps the official dataset fields, context selection, answer parser, and terminal
scoring behavior. It changes the execution harness:

| Pinned official code | This executable pilot |
| --- | --- |
| `RLMTrainEnv`, verifiers v0 | Native verifiers-v1 `OolongTaskset` |
| Official RLM-style subprocess REPL with `context` preloaded | Prime's built-in nano-RLM ACP/IPython harness with `context.txt` in its working directory |
| Explicit `rlm_query` proxy and iteration loop | nano-RLM at ref `4ef3438`, recursion depth 1 |
| Minimum-iteration/subcall metrics, with reward gating off by default | No artificial routine gate; only official OOLONG terminal correctness is rewarded |

Prime GRPO assigns the rollout's scalar terminal advantage to sampled action tokens across the
trainable trace graph. Thus parent and recursive model actions captured in that graph can receive
credit. This is not a root-only-loss experiment, and it should not be compared as if it were an
exact run of official `rlm_train`.

## CPU-only verification

The launcher is a `PYTHONPATH` overlay. It exposes official `rlm`, `rlm_train`, and `oolong`
without installing into or changing either clone or the Prime environment. The latter two remain
visible but fail with the documented v0 incompatibility; the runnable package is
`oolong_prime_v1`.

The launcher also prevents nano-RLM's installer from writing into the quota-limited home
directory. It fixes `UV_CACHE_DIR` to the project cache, fixes `UV_TOOL_DIR` inside the nano-RLM
cache, and exports `UV_NO_MODIFY_PATH=1` and `UV_DISABLE_UPDATE=1`. Before Prime starts, it accepts
the nano-RLM `.ready` marker only when `bin/rlm` is executable and the cached checkout is exactly
`4ef3438d55fdd39b18d34035833c73e13b006733`; otherwise it removes only that stale marker so
Prime's own setup can retry without deleting cached content.

```bash
cd /project/alex_phd/runs/rlm-research-r4/sidecars/official-rlm-prime-pilot-v1

CUDA_VISIBLE_DEVICES='' ./scripts/launch.sh smoke --dry-run
CUDA_VISIBLE_DEVICES='' ./scripts/launch.sh explore --dry-run
```

Both commands have already parsed successfully with the pinned environment, loaded the concrete
taskset config, and written resolved sub-configs. Unit tests load all 24 sealed rows, verify the
context-disjoint partition and data hash, test filesystem context injection, tie the ported scorer
to the pinned official source hash, and exercise official scoring behavior on golden cases.

## GPU launch

Wait until the current GPU owner hands off both devices and ports 8810, 8820–8821, 8910, and 5555
are free. Then run the systems smoke:

```bash
cd /project/alex_phd/runs/rlm-research-r4/sidecars/official-rlm-prime-pilot-v1
CUDA_VISIBLE_DEVICES=0,1 ./scripts/launch.sh smoke
```

Prime allocates the first visible device to inference and the second to training, so this command
maps physical GPU 0 to vLLM inference and physical GPU 1 to the LoRA trainer. The smoke performs
four optimizer steps, saves every step, and evaluates all eight held-out tasks at policy version 0
and again at step 4. Expected elapsed time is roughly 20–60 minutes after model and harness setup,
with a hard per-rollout timeout of 15 minutes.

Summarize it with:

```bash
/project/alex_phd/tools/uv-current/uv run \
  --no-project \
  --python /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  python scripts/summarize_run.py \
  outputs/qwen3-4b-oolong-rlm-smoke-v1
```

Launch the 25-step exploratory run only if all of these hold:

1. Both the step-0 and step-4 held-out evaluations finish, with at most one errored episode each.
2. At least one training cohort has unequal terminal rewards, hence nonzero GRPO credit.
3. The trainer reaches step 4, checkpoints exist, and updated LoRA weights are broadcast to vLLM.
4. No NaN, OOM, repeated harness-install failure, or systematic context-file error appears.
5. Ideally the step-0 exact-success rate is 20–80%. If it is outside that range, treat the smoke
   as a systems result and recalibrate the slice before interpreting learning.

Then:

```bash
CUDA_VISIBLE_DEVICES=0,1 ./scripts/launch.sh explore
```

The exploratory run saves at steps 5, 10, 15, 20, and 25 and evaluates the held-out set before
training and at step 25. Expected elapsed time is about 1.5–4 hours (3–8 aggregate A100-hours),
depending mainly on nano-RLM branch length. Stop early if task errors exceed 10%, every cohort has
zero advantage through step 5, or the trainer/inference weight versions stop advancing.

## Analysis and interpretation

Report the held-out exact-success rate and mean terminal reward before versus after training, with
all eight task-level outcomes. Also report train reward variance, episode error/truncation rates,
Python/RLM turns and branches, token use, checkpoint paths, and LoRA broadcast versions. Inspect a
small sample of successful and failed traces to learn whether the model actually reads and
decomposes `context.txt` rather than exploiting answer-format regularities.

This is a single-model, single-seed, two-context exploratory pilot. An improvement is evidence that
the end-to-end learning path works, not evidence of general RLM gains. A null or negative result is
still useful if the weight update and held-out evaluation are sound: it tells us whether to change
the task slice, reward, harness, or credit routing next.
