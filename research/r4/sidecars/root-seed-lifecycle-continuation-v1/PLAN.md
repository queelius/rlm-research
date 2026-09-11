# Independent-seed lifecycle continuation implementation plan

Goal: finish the already frozen seed981265001 eight-update question after a
non-model process-observation failure, retaining the original stopped attempt.

Architecture: a small parent driver imports the authenticated independent-seed
coordinator. It treats only FileNotFoundError/ProcessLookupError during process
inspection as an absent process. It creates a new output namespace with explicit
read-only-in-practice references to six committed rounds and three completed
validation exports. The unchanged state machine starts at validation6/round7.
Native collection, rewards, seeds, task inputs, Adam/RNG and selection stay fixed.

Source: original STOP-cc892fb4815740428c22431ac943efc4.json at
root-rlvr-independent-seed-v1/outputs/attempt-001. Trace reaches os.getpgid after
the inspected child exited. Process absence is already represented by None when
the original /proc existence check happens later; the intervening race is missing.

User's research-first operating rules override default worktree, broad tests,
commit and approval-pause gates. External namespace isolates accepted inputs.

- [ ] Add focused process-disappearance, permission propagation, inheritance
  boundary and deadline tests; demonstrate failure before implementation.
- [ ] Implement driver.py only; references preserve exact source paths/hashes.
  No automatic retry, no old STOP removal, no repeated optimizer application.
- [ ] CPU verify the actual six-checkpoint chain and unseen stage boundary; freeze
  source/input hashes and exact launch command in READY.json.
- [ ] Launch once on the empty owned GPU; checkpoint7/8 normally.3000-second
  inclusive exception budget,2880-second work clock, ordinary owned cleanup grace.
  This is a disclosed additional infrastructure envelope, not a new training seed.
- [ ] Audit combined lineage with original elapsed3432.94 seconds reported separately.

The two new updates and remaining validation/transfer answer the original question;
no recipe or selection changes are justified by interim validation2,2,1 out of8.
The original round7 has a generation manifest only, no collection or training.
