---
id: operator-dose-mechanism-qualification-20260910
status: resolved_by_additive_semantic_review
updated_utc: "2026-09-10T06:12:00Z"
scores_changed: false
old_artifacts_modified: false
---

# Correct answers, observed-map agreement, and correct computation are different claims

## Resolution at06:12 UTC

The additive exact-code review is complete:26 of29 strict successes are the
requested computations on actual child-label state, two use an incorrect user
scope that happens not to change the answer, and one recovers with a literal ID
after map overwrite. The five wrong child-error cases are confirmed across two
source-error contexts. No primary scores or original artifacts changed.
[Report](../../analyses/root-operator-dose-semantic-retrospective-2026-09-10/REPORT.md)
SHA61a9742c38adb10a219f1358c3a4a749b5a6664ee262557fa3694d900d6f08fd;
FINAL891c073261527297bb6609d13e81554f13e3de7acf4dc1a5987a88eea2bf541b.
MAIN read the report and verified all239 source and six analysis pins. The
reviewer authored the experiment implementation but independently reconstructed
the earlier dataflow analysis; this is not independent experiment authorship.

## Original qualification at05:56 UTC — preserved reasoning

The original dose readout still establishes 5/48 versus29/48 strict answers,
31/48 versus38/48 native finals, and actual child acquisition in1/48 versus48/48
endpoints. Its missing-outcome bounds and checkpoint/training integrity remain
unchanged. This note narrows the interpretation of the trace diagnostic, not the
primary score.

MAIN inspected the full sealed `dataflow_audit.py` after the composition audit
identified correct answers produced by wrong operators. The dose diagnostic
unions printed child-label maps, independently computes the requested scalar,
and checks agreement with the final and integers in tool observations. The
script itself warns that matching an observed integer does not prove which
program produced it, and that a host-side union is not model execution.

Those checks establish observed-map/scalar agreement. They do not by themselves
prove that the sampled program used the correct operator, target, scope, or
actually retained state. Therefore the stronger wording that all29 successes
were faithful task computations, and that five wrong finals were solely child
semantic errors, is provisionally suspended pending independent exact-code
review. They could contain correct-operation cases, wrong-operation
coincidences, literal recovery, or unresolved data dependence; the counts are
not assumed in advance.

Bridge is independently reviewing all29 strict successes and the five claimed
pure child-error cases, using actual programs and observations without
reexecution. Its report will be additive. Source report
`analyses/root-operator-dose-continuation-live-2026-09-10/REPORT.md`
SHA `c67c2b7430b69a890d9a51f0be14d3084fc45439210284fca1454708b84a749e`
and all prior seals remain unchanged.

Future summaries must separate acquisition, observed-map agreement, actual
map use, correct requested operation, and final correctness. A correct final
alone cannot distinguish the correct computation from a shortcut that happens
to agree on that input. This also limits interpretation of terminal-only RL:
rewarded correctness is not automatically evidence of learned decomposition.
