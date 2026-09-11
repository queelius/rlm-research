# Counterfactual-card96 independent audit

The frozen practical gate fails. Original strict score is5/24 in both U and P; counterfactual is
1/24 U versus2/24 P, while counterfactual availability falls18/24 to10/24. Manual review of all61
available traces finds five genuine requested computations, all in P: three original and two
counterfactual, with the two counterfactual computations both in one parent context. U has none.
The remaining eight strict successes are wrong-operation/scope, literal-recovery, or zero
coincidences.

There are35 NULLs:17 capped tool routes with no native final,17 over-context root HTTP400 terminal
attempts, and one other endpoint timeout. All1166 physical attempts and1149 choice completions were
reconciled; all61 native finals authenticate. See the full independent
`analyses/root-counterfactual-card-signatures-live-2026-09-10/REPORT.md`, `NATIVE_AUDIT.json`, and
`EVIDENCE.json`. No generated code was reexecuted or missing answer repaired.
