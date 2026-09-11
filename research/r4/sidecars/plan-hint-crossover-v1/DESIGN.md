# Supplied-procedure crossover, 2026-09-08

Ready exploratory comparison: does an explicit OOLONG procedure improve strict success,
inspection, executed Python, and recursive decomposition relative to a minimal task instruction,
under the **same coding/recursion-aware system prompt**? The experiment never launches a GPU
server; the operator supplies one already-owned local 4B endpoint.

The runnable seal is [SPEC.runtime-id-v2.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SPEC.runtime-id-v2.json"), SHA-256
`ec84dcd12665c86fd8284faa00f148800b9ae4890d680472a9865687b21487b2`.
The 56-row coordinate plan SHA-256 is
`d2e8df38adba7d9ce199797df72f86604092fa7d22789eb6b467e6377ad90698`.
The older SPEC.json and driver.pre-image-normalization.py preserve the prelaunch version.
Its literal image-ID comparison stopped before inference: rootless Podman reports a bare digest,
not the `sha256:`-prefixed spelling. The new version normalizes only that representation and
still rejects a different digest. Both versions select the identical image and coordinate plan.

## Exact intervention

The original strict taskset inherited this file instruction:

```text
The full context is stored in context.txt in your current working directory. Use the Python environment to inspect, parse, summarize, and decompose that file. Do not guess from the question alone. Return the requested final answer format.
```

The minimal arm replaces it with:

```text
The full context is stored in context.txt in your current working directory. Do not guess from the question alone. Return the requested final answer format.
```

The supplied-procedure arm uses the identical minimal instruction, then a blank line and:

```text
Suggested procedure: First inspect context.txt and parse each Date/User/Instance record. Read the aggregate question to decide which records and fields are relevant. If the answer needs only user IDs, count them directly in Python. If semantic labels are needed, partition the relevant records into batches, use recursive rlm calls to assign exactly one of the six labels to each record, store the assignments with record indices, then use Python to compute the requested exact aggregate. Check that every relevant record has one assignment before giving the final answer. Do not replace classification with keyword guessing.
```

The category-definition paragraph, literal final question and answer-format instruction, gold,
context bytes, task key, runtime setup, scorer, and task-level system_prompt=None are unchanged.
Full original and paired prompts and their native task hashes are in the runnable SPEC.
The sole changed TaskData field is `prompt`, tested against all fourteen actual task objects.
Removing the procedure paragraph from the supplied prompt exactly recovers the minimal prompt.
This is a bundled procedural-support intervention, not a clean isolation of batching, recursion,
coverage checking, or keyword-guess discouragement individually. There is no no-hint third arm.

The pinned nano-RLM system prompt still makes the model a coding agent, explains the persistent
ipython REPL, supplies `await rlm('sub-task')` and parallel `asyncio.gather` examples, and limits
built-in tools to one per turn. It does not contain the OOLONG parse/classify/aggregate procedure.
The input context also retains its existing instruction to calculate exact aggregate statistics.
Consequently “minimal” is **not free planning, tool-naive inference, or an unscaffolded baseline**.
The official pinned prompt/config/license snapshots, checksums and a real recorded system-message
hash are in [the audit provenance](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/2026-09-08-literature/plan-hint-prompt.HoZuFs/PROVENANCE.json").
The recorded message was from the training-client qualification; its shared harness system
content is distinct from that client's subsequently diagnosed assistant-prefill defect.

## Selection and provenance

Original data: `oolongbench/oolong-synth`, validation revision
`f0d59eaf0febf130664cfceb710436c8e3216b2b`. This reuses the already sealed
official-rlm-prime-pilot-v1 tasks.jsonl and selection.json, hashing their actual bytes.
The original source asset is `data/validation-00000-of-00009.parquet`, SHA-256
`a0420298223aaca11c702ffe6e9fdf773f27a99066a84e5e05c06d843214aca6`.
The source dataset's validation split is not confused with our operational train/eval split.

| Analysis split | Context window | Selected source IDs |
| --- | --- | --- |
| development / existing train | 8 | 12000008, 12000009, 12000010, 12000023, 12000024, 12000025, 12000029 |
| source-heldout / existing eval | 6 | 12000006, 12000007, 12000037, 12000044, 12000045, 12000046, 12000050 |

Both context groups contain one least-label task, two comparisons, three numeric label counts,
and one user-frequency task. Development IDs 12000014, 12000017, 12000020, 12000022,
12000026, 12000027 and 12000028 are omitted to match those task-type counts, choosing the first
eligible frozen source rows rather than selecting successes or failures.

Exclude 12000030 and 12000031 because their question supplies only `location` as an allowed
label; exclude 12000052 because it supplies only `human being`. These questions practically
reveal their answer without context inspection and are unsuitable inspection/planning probes.

Development and source-heldout have disjoint exact context hashes and context-window IDs.
The heldout context was already evaluated on September 2: it is disjoint from training but is
not a fresh confirmatory test set. There are **two independent context groups**, not fourteen
independent contexts or fifty-six independent scientific samples. Source rows within a window
are highly dependent. Selection is fixed before this crossover's outcomes.

## Pairing, requests, runtime, and cost

- Fourteen source questions × two arms × two paired seeds = 56 rollouts; temperature 0.5.
- Each task/repeat gets one deterministic seed shared by both arms. Pair order is randomized
  with Python Random(20260908); each task has minimal first once and procedure first once.
  Each pair stays adjacent on its worker. Four pairs run concurrently on the single endpoint,
  so global wall-clock completion order is not the dispatch order.
- Fixed evaluation client throughout; do not import the experimental corrected-training-client
  wrapper or change the renderer during this contrast. Both actual requests use top_p=1,
  top_k=-1, min_p=0, 2048 maximum completion tokens per model call, return_token_ids=true,
  cache_salt="0", no retries, and the same strict terminal scorer.
- nano-RLM 4ef3438, max_depth=1, no added skills; rootless image
  `sha256:53a70288e91a75c9bc8cbc9a75da4c3d156227266fd8c6c997deb8ef7f921552`.
  Setup/rollout/finalize/scoring caps are 300/900/60/60 seconds, episode cap 1020 seconds.
  The unchanged native execution policy includes a 64-subagent-call ceiling; there is no
  invented six-turn or fixed-total-token cap. The whole study cap is 5400 seconds with a
  60-second shutdown reserve; the launch command adds an external 90-minute cap and 90-second
  kill grace for stuck cleanup. A resume retains the original attempt deadline.
- Input-token counts necessarily differ because the procedure adds text. We equalize the
  generation and runtime budgets, not realized token use or prompt length. No meaningless
  padding is added. Cost is reported, including all retained root/child call records.
- Every completed or cancelled attempted episode gets an atomic immutable JSON checkpoint.
  Completed malformed policy terminals can earn strict zero; execution errors remain null.
  Stop above 50% execution errors after eight attempted episodes; malformed completed output
  is not an execution error. Partial pairs and unrun coordinates remain visible.

Metrics include strict reward and terminal validity, official score/disagreement, structured vs
executed ipython calls, first-action class, execution error types, model calls, tokens, cached
input, logical input (uncached prompt + cached), completion tokens, and episode wall time.
Execution-linked code markers identify inspection and attempted recursive `rlm` calls;
`sub_rlm_num_calls` supplies the harness's observed recursive-call count. A code marker means
a matching tool response exists, not that the cell finished successfully or that its result
caused the final answer. Inspection can be missed if a filename is assigned indirectly.
These are coarse behavior diagnostics, not proofs of faithful planning or novel decomposition.
All source traces are retained for targeted adjudication. No API dollar price is invented;
token counts and wall time are the cost measures. Summed episode wall time overlaps under
concurrency; STATUS records study wall time separately.

The baseline endpoint descriptor uses Qwen3-4B-Instruct-2507 revision
`cdbee75f17c01a7cc42f958dc650907174af0554` and its sealed zero-update step_0 LoRA. That is
not evidence of native RLM training. The driver hashes the actual task/scorer/client/harness
files, model manifest and tokenizer configuration, and adapter files. It does not demand old
archived checkout-wide seals or the vanished September 2 image. Public-source snapshots are
inspection inputs, not downloaded code executed by this driver.

## Launch and post-update replay

The existing server must advertise the frozen model alias and the API key must already be in
`STRICT_RLM_CALIBRATION_API_KEY`. The descriptor's historical client_path annotation is not
used to select the client; every frozen coordinate selects eval. Supply the actual warm
server's loopback URL if it is not port 18601. The URL override is frozen in ATTEMPT.json.

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout --signal=INT --kill-after=90s 90m /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/driver.py --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/SPEC.runtime-id-v2.json --endpoint-url http://127.0.0.1:18601/v1 --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/outputs/pre-update-001
```

Read-only CPU qualification uses that driver and spec with `--preflight` instead of the
endpoint/output arguments. It does not contact an endpoint or container. The separate actual
image-inspect check was run read-only and passed canonical identity normalization.

After RLVR, create a **new** endpoint descriptor with the post-update alias/path/checksums;
do not mutate the baseline descriptor. Freeze a distinct post-update spec:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/driver.py --prepare --weight-condition post_update --endpoint-descriptor /absolute/path/to/post-update-descriptor.json --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/POST_UPDATE_SPEC.json
```

Run with those same `--weight-condition`, descriptor and spec flags, a new output directory,
and the post-update server URL. Check the plan SHA is exactly the baseline value above before
launching; the source task/prompt hashes and seeds stay unchanged. The adapter descriptor must
provide actual adapter_config.json and adapter_model.safetensors SHA-256 values and the pinned
base-model manifest identity. The default actual model architecture is unchanged.

The resulting exploratory weight × hint comparison can ask whether training changes reliance
on supplied procedures, and whether any improvement extends from context 8 to context 6.
An improved minimal arm plus a reduced procedure advantage is consistent with internalizing
some strategy, but syntax adherence, classification, prompt sensitivity, and changed resource
use remain alternative mechanisms. A positive hint effect shows route-following support can
matter; it does not establish discovered decomposition. These two contexts do not establish
compositional transfer, broad co-adaptation, or an out-of-distribution capability claim.
Promote only after a fresh context-disjoint task slice and a more isolated strategy intervention.

## Focused verification

Five CPU tests passed (2.16 seconds): exact paired/seed counterbalance and disjointness;
prompt-only changes preserving questions; execution-linked inspection/recursion with all-trace
token accounting; null execution-error rewards; and image-ID representation normalization
that still rejects different content. CPU freeze, runtime configuration validation and client
construction passed; the read-only live image identity check passed. No GPU launch was made
by the preparing subagent. Ruff reports one 101-character documentation string (E501);
the frozen source was left unchanged rather than resealed for that cosmetic issue.
