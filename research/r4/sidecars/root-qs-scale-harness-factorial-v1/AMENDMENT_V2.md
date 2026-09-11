# READY V2 amendment

Pre-launch review found that `OWNER_RUN.json` would have named its deadline fields
`outer_deadline_epoch_epoch`, `owned_deadline_epoch_epoch`, and `work_deadline_epoch_epoch` because a
generic suffix was appended to already-suffixed internal keys. This did not affect runtime deadline
arithmetic, but it made the audit metadata wrong. A focused failing regression test was added, the
metadata projection was corrected, and this additive V2 seal supersedes `READY.json`. No selected
group, prompt, task, seed, binding, budget value, or scientific outcome changed. No GPU call occurred.

