# Independent restart48 audit method

Timing: written after launch and after partial output files existed, but before this auditor read any
restart outcome score, final answer, or model-authored program. This is not a prospective
preregistration. Frozen science inputs and already-existing output bytes are pinned separately.

Primary scoring is a full-strip `Answer: N` match against HOST_GOLD-derived counts. A returned,
natively authenticated malformed or length-capped final is observed zero; missing, unreturned, or
native-inconsistent output is NULL. The scientist summary is not the primary scorer.

For each of the 16 source states, independently verify three fresh Q/A/M sessions with the same
context, source state and seed. These are paired endpoints nested in 16 states, themselves built
from four previously exposed contexts; never count 48 independent contexts. Verify first-root
native prompt identity, root/child model identities, final branch/token/text/usage, setup bytes,
package equality across arms, and the source cut before corrective computation.

Actual state use requires executed model-authored code or an explicit final derivation tied to the
supplied artifacts. Mere filenames, AST mentions, metadata exposure, or scalar agreement does not
prove use. Record separately:

- canonical artifact retrieval: executed code reads a canonical state file and its returned tool
  observation is consistent with the frozen file;
- complete map merge: all source map pieces are loaded and combined without dropping keys;
- last-variable overwrite: repeated loads replace one variable and downstream reduction uses only
  the final piece;
- scoped reduction: actual code derives the requested record IDs and counts the requested target
  over the merged supplied predictions;
- quoted-state use: Q operationally parses or recreates the genuine quoted maps, not merely sees
  them in the prompt;
- reacquisition: any new depth>0 model call, kept distinct from use of the 40 historical calls;
- direct-record computation and unclassified/ambiguous paths.

Do not execute model-authored code. Audit only retained code, tool observations, files and native
records. For width4, the correct supplied-state count uses the disjoint union of all four maps; for
width16 it uses the single map. Preserve wrong predictions. Report dataset correctness and
supplied-map consistency separately.

Costs count every new root and child model request once from authenticated role captures, including
usage and latency where retained. Report canonical file retrieval/tool execution separately from
model calls, and setup/export time separately. The 40 historical child calls are shared physical
acquisitions; charging each source package to Q/A/M yields 120 hypothetical reused acquisitions,
not 120 new calls. No future/private/corrective/gold data may appear in packages.
