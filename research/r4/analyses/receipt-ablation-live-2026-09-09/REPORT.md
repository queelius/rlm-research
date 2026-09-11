# Receipt72: the new interface was not used

The unchanged historical prompt scored **21/24 exact final answers (87.5%)**.
Both indexed_raw and receipt scored **0/24**. Neither new arm made a child call,
requested a helper result, or accessed a receipt. The practical prompt packages
failed here; the value of an actually consumed receipt remains untested.

This is a fixed historical step8 root with the same c32de child, not a selected
checkpoint from the current independent-seed continuation. The frozen method was
written before outcomes; six exposed developmental contexts, two count questions,
two repeats form24 task/seed triples. All six arm orders occur four times.

## Final answers and paired comparisons

All72 scheduled episodes were recorded, execution-complete and observable under
the unchanged scorer. There were no infrastructure-null, unrun or budget-censored
episodes. Complete empty policy replies remain zero under the original contract,
but are explicitly separated below as unanswered rather than hidden in accuracy.

| Arm | Exact | Valid but wrong | Empty terminal | Nonempty malformed | Observable |
| --- | ---: | ---: | ---: | ---: | ---: |
| unchanged | 21 | 2 | 1 | 0 | 24 |
| indexed_raw | 0 | 5 | 19 | 0 | 24 |
| receipt | 0 | 20 | 1 | 3 | 24 |

Receipt minus indexed_raw has0 gains,0 losses,24 ties. Each new arm minus unchanged
has0 gains,21 losses,3 ties. No comparison is incomplete. Every one of the12 task
groups has at least one loss against unchanged; each of the six context groups
also loses. Unchanged context scores in context-index order0–5 are2,4,4,4,4,3 out
of4; both new arms are0 throughout. Repeat0 is12/12 unchanged versus0/12 each
new arm; repeat1 is9/12 versus0/12. All24 exact seed-level contrasts and all task,
context and repeat summaries are retained in AUDIT.json. These are descriptive
dependent observations, not72 independent confirmation trials.

## What the model visibly did

There are no helper request, result, error or receipt-access events. All48 new-arm
helper audit files were absent. Native-request corroboration is decisive about
the absence of child invocation: all144 root calls and296 child calls are linked
to episode traces, and **all296 children belong to unchanged**. Thus no strict
map was presented to the parser; map validity, subset coverage, returned order,
and result consumption are not applicable, not0%-valid maps.

The optional module was available:23/24 receipt episodes executed code using
source_records(). But20/24 included an `answer_category` reference and16/24 had
a visible KeyError in a root tool observation. The catalog intentionally exposes
only public ID/text and provenance, not hidden answer labels. A representative
root first filters `record['answer_category']`, observes KeyError, inspects the
actual public fields, and ends by saying the category is unavailable instead of
asking the child to classify it. Receipt returns the integer0 in15 episodes.

Indexed_raw executed root Python in5/24 episodes but never source_records() or
rlm_records();19 episodes ended with an empty reply. Unchanged executed Python
in23/24 episodes and made296 recursive calls. Receipt executed Python in23/24,
but neither new arm's executed root code contains rlm_records or await. These
are observable code/error markers, not proof about hidden reasoning or causal
mediation. Missing root-writable helper logs alone would not prove non-use; the
matching absence of actual native child calls supplies independent corroboration.

## Cost and terminal accounting

| Arm | Root/child physical calls | Actual input tokens | Actual action tokens | Sum of episode seconds |
| --- | ---: | ---: | ---: | ---: |
| unchanged | 49 / 296 | 310,298 | 17,994 | 1,334.16 |
| indexed_raw | 29 / 0 | 30,441 | 9,211 | 948.39 |
| receipt | 66 / 0 | 87,388 | 7,802 | 954.67 |

Totals are440 physical attempts,428,127 input tokens and35,007 action tokens.
Every retained physical attempt was linked; no unassigned attempts were found.
All actual responses were HTTP200. There was one length-finished call in unchanged,
none in the new arms. Cache measurements were absent in all440 trace calls, so
cached tokens are unknown, not zero. Token totals are reconstructed from actual
native request/action ID arrays and agree with trace usage and stored derived
totals. Summed episode seconds overlap under concurrency and are not job elapsed.

Collection took418.38s; owned driver elapsed470.42s and operation elapsed473.20s.
Terminal complete=true, no stop reason, no cap overrun. The owned release record
states all captured process identities exited; operation exit0, timed_out=false,
empty GPU PID list, no_retry=true. The operation-local lifecycle absence observer
wrapper is included in provenance; it changes no scientific arm.

## Independent checks and limitations

The audit reconstructed all72 exact plan/arm/task/context/seed identities and
all24 complete triples. It authenticated224 scientific/preparation closure entries
and245 accepted operation closure entries, including main's receipt wrapper,
amendment and pinned continuation observer. It checked frozen service binding,
phase plan, depth-to-alias mapping, adapter identity, sampling seed/temperature,
native prompt/action tokens, and the three terminal-marker hashes.

Host-only gold counts were recomputed from64 labeled records for each of12 tasks,
with768 task-record/group/text bindings checked against original public inputs.
Every terminal was rescored independently using its last nonblank line, one
permitted outer wrapper and the exact original numeric regex; all72 scores
match stored derived results and trace reward. A separate check executes only
the two pinned pure parser functions from the frozen scorer's AST and agrees on
all72 terminal parses. Runtime root_reply stripping is matched to the pinned
verifiers ACP implementation. No generated code was executed during this audit.

Three focused parser/unknown-accounting tests pass. Two short CPU audit attempts
stopped on auditor assumptions about the gold-hash scope and root_reply stripping;
both were corrected against frozen source before the complete audit pass. Their
details are preserved in AUDIT_IMPLEMENTATION_NOTES.md. A bounded supplement then
checked exact scorer semantics and separately counted unanswered replies; no
scientific retries, replacement data or model calls occurred.

New versus unchanged is a prompt-package effect: both new prompts remove the
familiar historical procedure/example. First-task prompt lengths are566 unchanged,
314 indexed_raw and349 receipt. Receipt versus indexed_raw adds availability plus
minimal consumption documentation, but neither was consumed. Do not infer that
strict validation hurts accuracy, or that a consumed receipt has zero effect.
Do not infer a training-specific defect without an original-root comparison.
The root-writable helper diagnostics could in principle be modified; no claims
from them were promoted to semantic validation. Adaptive child calls would not
automatically be paired even if helper uptake had occurred.

## Next decision, not an implementation

Prioritize a small competence/uptake check before helper SFT. Restore the familiar
procedure equally in raw and receipt arms, state the honest public catalog schema
explicitly (no answer_category/labels), and show one complete executable helper
call plus aggregation. Keep the root free after the demonstration. A balanced
original-root versus step8 comparison can then separate generic API teaching from
policy-specific prompt dependence. Include an unchanged reference if estimating
the package effect;144 episodes is the full two-root×three-arm extension of the
present24 coordinates. A smaller prospective sentinel subset can decide whether
any helper training is justified before paying for that full grid. Changing
multiple prompt ingredients without an equal raw/receipt control would repeat
the confound. No followup was implemented or launched by this audit.

Artifacts: METHOD.md and METHOD_READY.json retain the pre-outcome method;
AUDIT.json contains all reconstructed scores, contrasts, native linkage, events,
root code/observations and source hashes; SUPPLEMENT.json contains exact raw root
replies, unanswered accounting, frozen-scorer checks and accepted closure hashes.
audit.py, finalize_audit.py and test_audit.py reproduce these CPU checks.
