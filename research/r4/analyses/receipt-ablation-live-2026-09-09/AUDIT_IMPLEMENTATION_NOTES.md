# CPU audit implementation notes

The first audit invocation stopped before scoring its first episode: the auditor
incorrectly assumed TASKS.gold_sha256 hashed the complete host-gold object. Frozen
prepare.py line52 proves it hashes task.data.answer only. Corrected that audit-only
assertion to hash the host-gold answer string; still independently reconstruct
the integer from all64 source labels. No model retry or scientific artifact change.
The initial parser fixture collection failed because audit.py did not yet exist
(TDD red); after implementation all three focused tests passed.

Method wording clarification: “signed integer” means the original regex
`-?\d+`, allowing optional minus but not plus. The auditor preserves that exact
source contract. METHOD.md remains unchanged.

Second invocation found another source-semantics mismatch in the auditor's raw
terminal correspondence assertion: pinned verifiers/v1/acp/__init__.py line289
sets root_reply to turn.reply.strip(). The auditor now compares the terminal node
with that exact strip operation; final-line scoring is unchanged. Both failed
CPU passes stop visibly rather than silently discarding their assertions.
