# Four-needle ordinal-transfer evaluation

MAIN runs the two owners separately under the shared GPU lock, base then checkpoint32. Verify
`RUN_READY.json` and use its exact argv. Each owner has a 700-second cap and each external command an
800-second cap. Failure of one arm is preserved and does not redefine or retry the other.
