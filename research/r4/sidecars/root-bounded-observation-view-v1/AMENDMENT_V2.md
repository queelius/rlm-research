# Additive V2 visibility correction

V1 READY `a5a50377…` is preserved and rejected before launch. Its custom raw ledger was placed in the task working directory, where ordinary policy code could read it, contradicting the analysis-only claim.

V2 changes no scientific row, seed, prompt, task file, model, sampling, scoring, or clock. The engine's pre-existing `Session.log_tool_result` remains the sole complete raw-output record. V2 adds only hashes/sizes/cap/clipping metadata to that same session log and harvests the relevant session entries after rollout but before harness cleanup; it creates no raw ledger in task cwd. The system prompt advertises the conversation-log path, so this is not a filesystem access-control intervention: it isolates the passive next-request view, while deliberate policy access to the pre-existing log remains an explicit caveat.

The 4,096-byte setting is the retained raw-payload budget (head plus tail). Native warning text and the omission marker add visible-message overhead beyond 4,096 bytes. The 20,000-byte control continues to call the exact existing one-argument truncator.
