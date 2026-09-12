# AG News four-step true-HF arm

Status: conditional exploratory arm. MAIN may admit it only after current mechanics readouts; this
READY does not authorize launch.

Starting from the original c32 adapter, run four updates over four disjoint balanced 32-record AG
News steps. Each singleton receives four fresh temperature-1 rollouts. Preserve the reference
true-HF constrained sampler, immediate exact replay gates, RLOO, sequence-sum/128 loss, AdamW
LR1e-5, zero weight decay, clip1, carried optimizer, and step checkpoints. Stop rather than update
on any probability/support, zero-signal, timeout, or integrity failure.

The intervention bundles an AG domain/four-label change with 128 unique examples rather than the
reference arm's repeated TREC32. It is not a data-quality-only comparison. The full helper request
is replaced using the standard AG builder; no TREC definition remains in decoded prompts. Host gold
is absent from prompts and public files.

The owner cap is 4,200 seconds and external cap 4,400 seconds, revised upward from the reference
3,300/3,400 because AG texts produce longer prompts. The scientific dose remains exactly four
updates, 32 groups/update, four rollouts/group; a timeout is preserved as failure rather than
silently shortening examples or dose.
