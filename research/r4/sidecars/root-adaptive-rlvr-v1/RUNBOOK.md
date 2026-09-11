# Parent-owned adaptive RLVR handoff

CPU preparation does not choose starting weights and does not authorize a launch. PREPARED authenticates the executable/data closure; MAIN must inspect it and separately freeze exactly one start after interface-SFT readout. No source changes are needed for either supported start. Under no circumstances substitute a validation-best checkpoint or historical Adam state.

Environment: `/project/alex_phd/envs/prime-rl-5990b1b/bin/python` for coordinator/native collection; the fixed training interpreter in study.py for GPU optimization. MAIN supplies exactly one `CUDA_VISIBLE_DEVICES` assignment, existing inference API-key environment and inherited library paths, holds the shared accepted-operation lock, verifies the exact predecessor exited and GPU is empty, then launches. Preparation never queries or controls GPU/service ownership. There is no independent auto-waiter here.

From this sidecar directory, CPU verification:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python coordinator.py verify
```

After the SFT readout, MAIN may prepare either unapproved candidate:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python bind.py --kind interface_sft_final4 --output /ABS/NEW/START_CANDIDATE.json
```

Use `--kind historical473210` only if MAIN explicitly chooses that alternative. Candidate construction authenticates exact member hashes but always writes `approved:false`. MAIN publishes a separate immutable START_BINDING.json with `approved:true` after deciding; parent acceptance must bind its bytes/hash alongside PREPARED and CAMPAIGN. The final4 path is exactly the accepted local-runtime attempt's training/RESULT.json, fixed checkpoint-0004 with SFT state identity/epoch2/cursor0; final score files are not dependencies.

Parent launch (no activation/install, no extra service):

```sh
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-adaptive-rlvr-v1/coordinator.py run --start-binding /ABS/MAIN/START_BINDING.json --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-adaptive-rlvr-v1/outputs/attempt-001
```

Maximum parent process envelope 7230s. One shared work clock7080s +120s owned cleanup gives7200 inclusive. Collect16 training slots per round with four workers (1200s cap), validation8 and transfer16 stage caps900s; service readiness180s; actual model-load/update600s with750s subprocess envelope bounded by remaining work. Native episode setup/rollout/finalize/scoring remains45/300/15/15 seconds and max2048 completion,8192 context, root T.5/full support. These are inherited accepted SFT budgets, not a promise every episode finishes. Same exact local image/storage wrapper, no network setup or persistent-store fallback added.

The sole service exposes current root + fixed c32de child. Qualified PID/start/UID/PGID/descendant ownership, known Prime title and vanished-/proc handling are reused. Service and descendants are released before each optimizer subprocess. The final tiny summary writes only after final service release; independent raw audits run outside this ownership operation. Every step persists exact adapter/optimizer/RNG/correction/input state immediately. Outputs: RUN, round-NN/{GENERATION,collection/{rollout,export},training/checkpoint-N,COMMIT}; validation-00/04/08 and transfer-00/08; services/* ownership/release; fixed SELECTION and FINAL, or immutable STOP.

`resume` in place uses the original deadline and exact START_BINDING/GPU. It authenticates committed checkpoints and will not repeat updates, reroll incomplete stages or continue a terminal STOP. A partial failed training/capture requires a new explicit decision, not an implicit retry. Frozen earlier experiments, raw failures and checkpoints are never edited.

Interpretation: report binary/null totals on planned denominators plus actual admitted mixed groups. A completed final may be diagnostically scoreable despite an episode/finalize failure; it is still null for this campaign. Child grammar is verified at the typed wire hook and remains uncredited. Sorted saved dictionaries alone do not re-prove grammar key order; ordered schema strings and the qualified pretransport assertion carry that narrower evidence. Fake-provider CPU fixtures cannot become scientific likelihood records. No cost-shaped reward, forced helper, semantic repair, crop or positive-label fabrication.
