---
schema: scale64-zero-support-and-acquisition-note-v1
status: additive_manual-judgment-qualification_no_reinterpretation
sealed_semantic_audit_sha256: 55c859318389ba8c62f95db86441755e8e21486764d6ac19cdfba7491a6c56b0
sealed_native_audit_sha256: 7501e4fb6adbec63de9ebee98643a038c38de3b172d7f236a7f74e8c4eb61f0b
---

# Zero-support and acquisition qualifications

## Two actually successful but non-general algorithms

Endpoints `7aa323ae…` and `548588e9…` each acquired and retained the complete 16-record decoded map,
identified qualifying users, and then executed the requested target-B selection as a Python
set-comprehension over record dictionaries. In both realized traces that selected collection was
empty. The parent-linked tool observation is exactly `0\n` with no exception, and each authenticated
final is `Answer: 0`.

Their existing `faithful=true` judgments are therefore preserved under the frozen **actual executed
path** rubric. However, the implementation is not a generally valid algorithm: if any target-B record
had been selected, inserting a dictionary into a set would raise `TypeError: unhashable type: 'dict'`.
These are “actual-path faithful on empty selected support,” not evidence that the generated reducer
would work on a nonempty selected set. This qualification applies to 2 of the 12 faithful paths and 2
of the 7 faithful-plus-strict paths.

## Zero versus nonzero gold

Gold zero occurs only in 12 size-16 planned cells. Their planned-denominator accounting is 11
authenticated / 1 NULL, 8 strict correct, 3 observed wrong, 6 faithful, and 6 faithful-plus-strict.
The other 52 cells have nonzero gold: 27 authenticated / 25 NULL, 1 strict correct, 26 observed wrong,
6 faithful, and 1 faithful-plus-strict. Thus 6/7 faithful-plus-strict successes are zero-gold cases;
the sole nonzero faithful-plus-strict success is `b8a0a3c2…` at size64. This is a major support
limitation, not a post-hoc change to any row judgment.

## Why row i19 has physical map coverage but acquisition=false

Manual row i19 is endpoint `108ede33…` (sft6, cumulative-4096B, cluster1, size64). Its episode contains
a genuine child assistant response encoding all 64 labels, which is why the audit-only physical child
diagnostic reports union coverage 64 and 55/64 oracle agreement. The root program did not successfully
decode that response into usable state: it passed record dictionaries, rather than record-ID strings,
to `strict_map`, and the root-visible tool observations are `TypeError` traces. Later retries repeat
the same interface error; there is no decoded complete map in root state and the authenticated final
is empty.

Accordingly, `acquisition=false` means **no successfully decoded child label map became available in
root execution state**. It does not mean the physical child failed to emit label-shaped text. The
physical child diagnostic and root-state semantic acquisition intentionally measure different
boundaries.

No producer output or sealed audit artifact was modified for this note.
