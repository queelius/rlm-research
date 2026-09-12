# Additive V2 repair

The unlaunched V1 READY and sources are preserved. Review found that the inherited owner and
collector expect `inputs.held.schedule_sha256`, while V1 flattened that field, and that the
study facade omitted inherited `load` and `source` functions used by role-hook and runtime-path
setup. V2 restores that exact interface and binds the emitted collector command to
`collect_v2.py`.

V2 also closes the checkpoint qualifier over the serialized initial tensors, initial RNG,
saved clipped gradient, both state/result/commit links, both post-update likelihood inventories,
and the result-linked 10x branch relation. Scientific inputs, branches, seeds, metrics, and caps
are unchanged.
