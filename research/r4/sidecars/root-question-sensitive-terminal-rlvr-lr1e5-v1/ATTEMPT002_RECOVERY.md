# Attempt 002 binding recovery

Attempt 001 terminated before any collection or optimizer update because the lazy qualified
collector called `terminal_common.starting_decision()`, which requires this sidecar's local
`START.json`; that file was absent. The same missing binding also prevented its fixed-last readout.

Attempt 001 is retained under `outputs/attempt-001`. Its `OWNER_TERMINAL.json` SHA-256 is
`4052d9a3ed386c5910672b0e02a0ebdf9e2e7a5738f0bcab5b6c20a9d344194f`; it reports incomplete,
released ownership, 192 planned training rows and 72 planned readout rows. The exact parent EXIT
SHA-256 is `db040cb03167ac10d6f466855e4a9633caa1851c6c7ebac0f55cb36aaf5eb48d`; exit code was 1,
elapsed time 3.341997876763344 seconds, no timeout, and no GPU processes after exit. Therefore it
contains no scientific intervention or endpoint outcome.

Attempt 002 adds the byte-identical authenticated `START.json` from the qualified recovery-v2
source (source SHA-256 `8cf856266ec2be5e2a1c9cc2a496cec84302519e710ecb16d282fa1525319404`), moves only the output
namespace to `outputs/attempt-002`, and assigns a distinct campaign provenance namespace. All JSON
files under `inputs/` and the LR recipe are unchanged. Superseded attempt-001 campaign, review, and
READY seals are retained under `superseded/attempt-001-missing-start/`.
