# The three adaptive-RL nulls are between-cell broker-control failures

Bounded read-only diagnosis, September9,2026. **The observed30-second timeout is not a per-cell recursive-work limit.** All three traces fail while setting the broker scope for a new root IPython cell, before that cell is dispatched. The previous child call has already returned and its map appears in the completed root tool observation. The immediate failure is a missing Jupyter shell reply to a tiny control command. Why that reply failed to arrive is not established by the saved artifacts.

This is an availability problem in the executed external Prime/nano runtime, not in this repository's unused core executor. The original three infrastructure/admission NULLs and their raw empty endpoints remain unchanged. No fix, reroll, model request, runtime fixture, live-outcome inspection or accepted-source mutation was performed.

## Executed source, not an approximate local implementation

The accepted runtime is image `8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c`, OCI manifest `a4c710e9…`, source commit `4ef3438d55fdd39b18d34035833c73e13b006733`. Its frozen installed-provenance record authenticates the actual committed layer source. The audit read the image-layer checkout and matched these complete file hashes:

| Source | SHA256 |
|---|---|
| `src/rlm/tools/ipython.py` | `8a150675a8b4c0642a656866db6d8f9a1de6e3263371e573e744d2cdd5cd5757` |
| `src/rlm/engine.py`, before role overlay | `2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed` |
| `src/rlm/broker.py` | `dd966afe72795fe2beb18b9a691194488c9ea365fa6886833d4be06d5106852e` |
| `src/rlm/supervisor.py` | `1b9a1b303b7c2a389d8981d0c7ea9d3e5603b49f8a420f354220c6a28c9cc78e` |
| `src/rlm/acp.py` | `dcf0b42dc4a8a23991be67c96275b9d28e5b8746f38d3024089a2e22beff4e59` |

Installed versions: IPython9.17.1, ipykernel7.3.0, jupyter_client8.10.0, jupyter_core5.9.1, pyzmq27.2.0, nest-asyncio1.6.0. The role overlay changes engine line offsets; saved traceback line489 corresponds to the scope-setting statement at original line485. Source inventory/provenance and raw excerpts: [EVIDENCE.json](../../../../ARTIFACTS.md#unpublished-files "Not published: EVIDENCE.json"), [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json").

## Exact call path and the distinct deadlines

1. Engine `_run_loop` opens a supervisor scope for a sampled root IPython action. `repl.set_broker_scope(scope_id)` is called synchronously **before** `asyncio.create_task(asyncio.to_thread(tool.execute,…))`. [Pinned engine, line480](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/2026-09-08-literature/leaf-contract.7HPUr5/nano__engine.py:480").
2. `IPythonREPL.set_broker_scope` calls `_execute_silent("_rlm_broker.set_scope(...)")`; this sends a silent kernel execution and calls `get_shell_msg(timeout=30)`. It does not use the cell's configured timeout. [Actual image IPython source, line338](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/runtime-images/rpi-v2.kCaOH4/root/vfs/dir/b50ce4f5b31918d4d2b15d21586825a9320f10fc20818b76f982bcd465d75efc/tmp/vf-rlm-4fa91253816bfa64435b7b727ec01bac2a7a7a2b72ece29ceb2474d26f95418d/checkout/src/rlm/tools/ipython.py:338").
3. Broker `set_scope` itself merely assigns `_scope_id`. It performs no child invocation or network RPC. Real recursion is a separate async `broker.run`→`_request` path. [Pinned broker, line117](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/2026-09-08-literature/recursive-example.6xBrmx/src__rlm__broker.py:117").
4. The Jupyter shell-channel read polls its socket for the supplied duration and raises `queue.Empty` when no message is ready. The exception is uncaught on scope setup, propagates through ACP as Internal error, then becomes a Verifiers HarnessError. It is not a provider HTTP error.
5. Ordinary cell execution uses a separate deadline inside `_execute_locked`, catches short IOPub polling `Empty` exceptions and continues; genuine cell timeout interrupts/recoveries and emits an explicit `[execution timed out after …]` tool result. None of those indicators occurs in these three traces. [Actual IPython source, line401](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/runtime-images/rpi-v2.kCaOH4/root/vfs/dir/b50ce4f5b31918d4d2b15d21586825a9320f10fc20818b76f982bcd465d75efc/tmp/vf-rlm-4fa91253816bfa64435b7b727ec01bac2a7a7a2b72ece29ceb2474d26f95418d/checkout/src/rlm/tools/ipython.py:401").

The engine's finally block closes the scope and attempts a second silent scope reset toNone, swallowing/logging reset failures. [Engine, line518](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/2026-09-08-literature/leaf-contract.7HPUr5/nano__engine.py:518"). Supervisor close_scope cancels/joins any remaining child tasks; it is not a30-second child policy. The primary saved stack points to **scope opening**, not this cleanup block.

## All three saved cases

| Case | Completed work before failure | Blocked next action | Physical calls / HTTP | Tail after last provider response |
|---|---|---|---|---:|
| round1 `d293bdeb…`, seed981298106 | First4 helper returned and map printed | Second root cell, intended filtering/classification | 2root+1child, all200 | 61.751s |
| round8 `7e51a0af…`, seed981298217 | First4 helper returned and map printed | Second root cell, intended all64 classification | 2root+1child, all200 | 64.158s |
| transfer0 `a8a65fb8…`, seed981298704 | First4 helper returned; second root cell returned a KeyError observation | Third root cell, intended record inspection | 3root+1child, all200 | 61.390s |

Raw paths, exact hashes, all calls/timestamps and tool observations are in [EVIDENCE.json](../../../../ARTIFACTS.md#unpublished-files "Not published: EVIDENCE.json"). All three graphs end with a sampled root IPython action with no resulting tool observation. The error precedes dispatch of that last cell. No second child attempt exists in any of them. The previous child call completed in well under a second of provider time; the first helper had already printed the returned map.

The two training cases contain problematic or potentially problematic sampled plans, but this does not make the blocked action an observed policy failure: round1 filters questionIDs by a user prefix, while round8 requests all64. Transfer's prior KeyError is an observed recoverable code error; the intended recovery inspection never executes. These distinctions matter when deciding training admission. They do not justify converting the nulls into failures or successes.

The61–64second tails are consistent with a30second setup wait plus another30second reset wait and cleanup. This is **an inference**, not two instrumented timeout timestamps: the retained traceback does not independently log the second timeout. No speculative wall-clock subtraction is presented as exact kernel scheduling evidence.

## What is established, and what is not

Established: a control-plane timeout can abort an otherwise active trajectory after a completed cell, irrespective of provider success. The30seconds is hardcoded to setup/scope synchronization, not an intentional recursive-cell execution allowance. It applies before the next action, not to a running child in these cases. The failure compromises availability and removes two training episodes plus one transfer episode from admitted data.

Not established: a slow but legitimate child was interrupted by this30second limit; loss of a provider response; dropped model action tokens; kernel death; a particular Jupyter/ZeroMQ defect; resource contention as the cause; or that increasing30 to300 would repair the experiment. We have model/call/graph records, not kernel shell/IOPub message logs or kernel liveness at the failure instant. Source inspection cannot recover that missing evidence.

One concrete source weakness is worth isolating: `_execute_silent` discards the request ID returned by `execute` and accepts the **next** shell message without checking `parent_header.msg_id`, reply type or reply status. The ordinary execution final drain likewise reads one shell message without correlating it to its own request; `_wait_for_idle` also accepts idle without parent matching. This permits stale replies to be mistaken for current control acknowledgements at the source level. It is not proof that stale-message consumption caused these particular timeouts. Scope synchronization also runs on the engine event loop while normal cell work runs in a worker; a diagnostic should record this boundary rather than assume it is causally harmless or conclusively broken.

## Smallest useful regression/reproducer, before any fix

First use a model-free fake kernel client against these exact three methods: provide a stale execute_reply before the correct scope reply, verify that the existing code accepts the stale message, then assert the desired behavior correlates request IDs and validates reply status. Separately make the shell channel raiseEmpty during scope setup and confirm the current propagation/finally path, without real30second sleeps. This tests a material control contract; it does not reproduce the observed kernel stall.

Then, only if MAIN authorizes a new owned CPU fixture, run the exact installed runtime with an operator-authored root→child→root sequence and a fake child backend. Include (a) a35second legitimate child inside a cell whose configured deadline exceeds35seconds, (b) successful child→next cell, and(c) recoverable KeyError→inspection. Record sent execution IDs, shell/IOPub parent IDs, status, thread identity and kernel liveness around scope open/clear. Start one worker; repeat the same bounded fixture with the production four-worker shape only if needed. No model weights or sampled host code are needed. Expected healthy behavior is that the35second child is governed by the cell deadline, while scope assignment remains a short matched control exchange.

Do not start by raising the timeout, adding silent retries/restarts or swallowingEmpty: those could hide reply misassociation, reset state, change likelihood/context continuity or change which trajectories are admitted. A fix requires evidence distinguishing delayed/missing acknowledgement, stale message correlation and kernel unavailability, followed by a new qualified source version. Existing accepted experiments and scores remain sealed.

Diagnosis scope is complete; underlying missing-reply cause remains unresolved. The extraction script exited0 and authenticated the three frozen raw files plus actual image source hashes. No runtime reproducer was run in this read-only task. Success-SFT outcome inspection remains gated on MAIN's separate trigger.
