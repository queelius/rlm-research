# Fresh-context result-observability comparison

## Question

When the root has computed the right scalar, does submitting it atomically remove a material
failure between Python state and the final answer? This is separate from whether the root selected
the right scope and whether the helper labels are correct.

Repeating the old “remember to print” target alone is weakly identified. The exact QS6 corpus already
contains 144/144 printing Python actions, yet the live policy produced four silent reducers and two
wrong `u0,u1` scopes. The next comparison should teach the same correct reducer in both learned arms
and vary only how its scalar becomes the final response.

## Existing contract being tested

The core RLM already exposes `FINAL_TEXT(text: str)` and `FINAL_RESPONSE(response)`. For this
plain-text task, `FINAL_TEXT` is the relevant path. It accepts only an already formed string, permits
only one submission, and cannot coexist with an exception or host failure. A valid submission ends
the branch immediately; it is not serialized as a controller observation and does not require a
later model turn. By contrast, a successful cell without a submission yields a typed observation
whose `execution.stdout` carries printed output and whose submission status remains absent/required.
Thus the atomic arm is an existing-ABI use and **not a novel API**. It also intrinsically removes one
model turn, so call and token costs must be outcomes rather than assumed equal.

## Frozen comparison

Before any model scoring, select ten label-blind AG test context groups of 16 records, excluding all
known local exposure manifests and the eight contexts in this audit. Six groups are train-only and
four are held readout groups. Each group has two questions: one all-record query and one rotating
two-user query, balanced between count and weight-sum operators. This retains familiar operations
while making the demonstrated scope mistake measurable. It is new local context evidence, not a
claim of absence from base-model pretraining.

Acquire one complete, question-blind c32 helper map per context using the unchanged typed 16-record
contract. Freeze and replay that same authentic map across root arms. This is a controller mechanism
control, not a deployable end-to-end latency comparison; report the shared acquisition cost and the
logical replay separately. Host gold never enters a root prompt or child request.

Start three root arms from the exact QS6 checkpoint:

1. **Unchanged QS6:** no new optimizer step.
2. **Print then submit:** four fixed SFT updates over all 12 train trajectories. The authored reducer
   uses the exact requested scope, ends in `print(value)`, and the next authored root action calls
   `FINAL_TEXT("Answer: N")` from the visible scalar observation.
3. **Atomic submit:** same train contexts, ordering, optimizer, learning rate, and four updates. Every
   authored action before the reducer is byte-identical to arm 2. The reducer differs only at its tail:
   `FINAL_TEXT("Answer: " + str(value))` replaces `print(value)` plus the later terminal action.

Training targets are computed from the authentic helper map, not host-gold labels, so the model is
taught faithful reduction of what it received rather than a hidden correction. Prompts, helper/tool
actions and observations are masked. Report root-action and terminal target tokens separately because
the two arms cannot have identical token doses. Use fixed checkpoint 4 only; do not select an
intermediate checkpoint from readout results.

Evaluate all three roots on both questions from all four held contexts, with the same map, root seed,
temperature, turn cap and executor limits. Preserve every malformed, finite-horizon and infrastructure
failure separately.

## Readout

Primary mechanism outcomes are:

- map-consistent endpoint: submitted integer equals the trusted intended-scope reduction of the frozen
  helper map;
- scope fidelity: generated reducer uses exactly the users requested by the question;
- result delivery: scalar was printed into a typed observation or atomically submitted, with no silent
  assignment;
- endpoint correctness against host gold, reported separately from map consistency;
- root/child calls, tokens, observation characters and wall time.

Static code remains inert. Recompute only a narrow allowlisted count/weight reducer with explicit host
loops; unsupported programs stay unknown.

Promote atomic submission for a larger replication only if it adds at least three map-consistent
held endpoints over print-then-submit across at least two of four context clusters, does not reduce
scope fidelity, and does not increase invalid submissions. If both trained arms improve scope over
unchanged but atomic does not beat print, the useful intervention is procedural scope training, not
the return channel. If atomic fixes delivery while both arms retain scope errors, pair it later with a
separately tested reducer representation. If neither arm improves two context clusters, retire this
tiny dose rather than expanding it post hoc.

