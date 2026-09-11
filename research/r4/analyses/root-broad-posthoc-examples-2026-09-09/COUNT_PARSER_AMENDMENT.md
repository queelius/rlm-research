# Analysis-only correction before publishing count-distance results

The first count-screen script incorrectly assumed the whole response had to be
one ASCII Answer line. Its three small tests passed, but comparison to sealed
primary outcomes stopped on original episode9e17aeab17ee1b6072c823912687a64ce2653a25e22d6357b049431739e394ed:
a long explanation ended in Answer: 0 and received its declared correct score.
No COUNT_SCREEN output was published before the assertion stopped the script.

Main then read the complete frozen scoring.py. Its numeric contract uses the
last nonblank line, permits one markdown wrapper, case-insensitive Answer,
whitespace, a negative/Unicode-digit integer and optional period/exclamation.
Those are inherited scoring rules, not new output repairs. The additive regression
failed first, then the diagnostic parser was changed to independently match that
contract. Original primary outcomes, samples, scores and training are unchanged.
The failed source is preserved as count_screen_initial_failed.py. Some raw files
are reread for this CPU diagnostic; no model or generated program is executed.

Count distance remains a post-hoc secondary description conditional on a numeric
terminal. It does not make nearly correct counts into successes or prove that
individual returned labels were correct. The frozen primary13/48 and16/48 and
numeric coverage are reported alongside it.
