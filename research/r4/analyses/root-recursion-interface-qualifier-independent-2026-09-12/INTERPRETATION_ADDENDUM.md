---
schema: root-interface-interpretation-addendum-v1
created_utc: 2026-09-12T12:35:00Z
status: posthoc_mechanism_diagnosis
changes_frozen_gate: false
changes_original_report: false
decision: no_larger_same_interface_rerun_yet
---

# Read the 4/6 result narrowly

The explicit-interface qualifier produced four correct final answers with a
helper available, versus none without one. All six helper-enabled answers were
available; one no-helper answer was unavailable. The frozen qualifier still
failed because both conditions repeated identical Python actions. This small,
research-exposed comparison is not an established benefit of recursion.

Two details from MAIN's inspection of all six enabled traces matter:

- The successful J2, M1 and M2 traces obtained a keyed label map and printed a
  scalar after executing the corresponding filtering or grouping calculation.
- T1 eventually obtained helper labels and printed the correct scalar zero,
  but its calculation was not faithful to the requested operation. Its final
  expression sums every record's weight for a user and applies a category test
  outside that sum. The `record` in that test is the stale last record from an
  earlier loop, rather than each record being summed. This computes the wrong
  function even though this particular output matches the answer.

A simplified illustration of that defect is:

```python
# Wrong: the test uses a stale `record` and does not filter the summed rows.
total = sum(row["weight"] for row in user_rows) if labels[record["id"]] == target else 0

# The requested operation would filter each row before adding its weight.
total = sum(row["weight"] for row in user_rows if labels[row["id"]] == target)
```

Do not silently change the frozen endpoint score. Keep 4/6 correct finals, and
report this separate process limitation. The static audit does not by itself
establish that all other helper labels or end-to-end procedures were correct.

# The import counter is deliberately narrower than its short label

The original analyzer's `bad_import_attempts` counts the exact source substring
`from rlm import rlm`. It is zero in this qualifier. That does **not** mean all
invalid RLM import attempts disappeared: the no-helper T2 trace repeatedly
executes `from rlm import reply as rlm_reply`, which raises ImportError. Its
longest identical-action loop has 18 consecutive repetitions. The broader
interpretation “no invalid imports” would be wrong; the existing numeric field
and gate remain unchanged.

The no-helper condition also keeps trying an unavailable `rlm` callable instead
of reliably adapting to direct classification. It therefore measures this
delegation-trained controller's behavior when a familiar tool is removed, not
the best possible direct-solving policy.

# Follow-up priorities

The separate MRCR root-procedure calibration does not depend on this qualifier.
Before spending on an expanded TREC comparison, test a targeted change that
addresses state/use errors—for example, explicit initialized input handles or
a small declared set of data operations—and compare against the current clear
Python instructions. Such a change must leave model decisions and raw evidence
access visible; it must not supply the answer or silently repair a failed plan.
Any later result should report correct answers and faithful computations
separately, preferably with a counterfactual input check.
