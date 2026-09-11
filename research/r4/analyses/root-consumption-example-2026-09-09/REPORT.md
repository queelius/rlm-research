# The root faithfully reported its program's zero

This is one posthoc-selected exposed failure, not a prevalence or treatment estimate. Episode `7eea21d9caec…` does **not** show a root model seeing14 correct labels and ignoring them. It shows the root writing code that mishandles text, observing that code's0, and faithfully submitting `Answer: 0`.

The distinction is concrete:

- **Available to the REPL:**13 completed child returns cover all64 records exactly once (twelve batches of5, then4). Each return is JSON-array **text**, such as `["location", "human being", "location", "entity", "description and abstract concept"]`. Host-only decoding finds14 human labels, equal to gold, with zero target FP/FN. Overall61/64 labels are correct; the three other-class errors do not affect this task.
- **Consumed by the program:**root trace node2 uses the following lines without any `json.loads` call:

  ```python
  batch_labels.extend(child.answer)
  human_being_count = batch_labels.count('human being')
  human_being_count
  ```

  The pinned API defines `RLMResult.answer: str`; the broker serializes/validates that result, not a decoded application-level list. Extending a list with these strings adds1,210 individual characters. No individual character equals the whole string `human being`, so the count is0. This is a deduction from recorded code, the return contract and matching observation—not execution of the generated cell by this auditor. No Python-heap/IPC payload dump was saved.
- **Visible to the root model and submitted:**node30 is the tool observation `0\n`; node31 is `Answer: 0`, with finish reason `stop`. The recorded root causal message path is nodes0→1→2→30→31. The13 child arrays are linked as semantic dependencies, not printed as root tool observations. The model therefore reports its own program's result; it does not directly consume those64 labels in a subsequent model turn.

Evidence supports a **model-generated consumer/type-contract error**, not a demonstrated material harness transport defect. The runtime's documented text return is consistent with the code and observed result; no child error, truncation or missing return was recorded. The case used the original857a7 root and c32de child, ChatEval, T=.5, seed2141929644:15 model calls, one executed cell,41.65s. Original rewards/usage remain unchanged.

Evidence pointers: [raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-composition-transfer-v1/outputs/attempt-001/episodes/7eea21d9caec13976bd381755cc1aa513e92e1fe7c81ee522b8b4fadeaa9b8a3.json"), JSON paths `episode.traces[0].nodes[2]`, `[30]`, `[31]`, and child terminal nodes5,7,…,29; raw SHA `b88bf60a8bb772d2f24ec956e83de4448da18e6f88a8034e6ab71375883f526c`. [EVIDENCE.json](../../../../ARTIFACTS.md#unpublished-files "Not published: EVIDENCE.json") contains exact code, child strings/record mappings, source hashes, routing-audit paths and original metrics. The cached nano revision is `4ef3438d55fdd39b18d34035833c73e13b006733`: `types.py:259` declares the text result, `broker.py:92` serializes it, and `engine.py:531` forwards the cell's output to the root conversation.

Uncertainty remains explicit: this ChatEval trace retains no physical token IDs/logprobs. All13 child initial/terminal internal-message hashes match their caller audits, as does the first root call. The final root call's internal-dictionary hash differs from its caller-message hash; exact physical-prefix identity is unavailable. Do not claim a byte-identical replay or universal transport proof from these records.

## Smallest useful follow-up—not implemented

Prefer a fresh paired instruction ablation with unchanged root/child weights, client, tools and budgets: original instruction versus the single explicit contract, “The returned `.answer` field is text. JSON array text must be decoded with `json.loads` before list operations.” For example, three prospectively selected fresh context compositions×two new seeds×two conditions gives12 trajectories. Freeze source groups/prompts/seeds first; measure actual decoding/type handling, target membership when observable, computed-versus-submitted count, strict reward and all-call cost. Do not add answer repair, fallback, oracle values, mandatory recursion shape or a new reward.

A saved0→14 tool-observation swap would instead test **final reporting under changed evidence**. It cannot demonstrate that the live interface or generated program improves. This episode has no qualified full-state replay seam before `extend`: all13 calls and the bad count occur inside one cell. Nano's `prompt()` preserves a *live* kernel, while `execution_snapshot()` records metrics/limits/edges, not a restorable heap; `run()` closes the engine. The existing MRCR paired finalizer demonstrates a live final-call boundary, not persisted REPL restoration. A text-only final-continuation experiment could be qualified separately, but this record's final-prefix identity is insufficient to call it an exact replay now.

No GPU/model calls, generated-code execution, replay implementation, prompt/reward/source/queue changes, or other episodes analyzed. The new read-only audit and its assertions completed successfully within the15-minute CPU cap.
