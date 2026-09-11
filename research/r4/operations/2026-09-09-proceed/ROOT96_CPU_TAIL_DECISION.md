# Release the completed root96 operation's redundant CPU tail

Decision September 9, 2026, approximately04:35 UTC, by main under the user's
standing autonomous research authority. This is not an outcome-based stop.

All96 planned episodes are saved; both48-episode phases report no stop or budget
censoring. TERMINAL.json says complete=true, error=null and elapsed1064.096s.
Its SHA is e716474a5e77ab14e66c4a4b9c2244aa322e30ed049a85427a2ccf841ce13be4.
Both owned service-release records exist. The GPU process list is to be checked
again immediately before action. No new root outcome totals were consulted.

The driver2144297/start1073086090, UID1523821556/PGID2144297, has no children.
It is doing post-release CPU analysis while the enclosing parent2120762 still
holds the shared scheduling lock. At04:33 its open files included the saved
step8 optimizer.pt, with no output ANALYSIS.json. Source analysis.py calls
study.verify_phase for each of96 episodes; that reauthenticates the parent and
phase source closure. The parent closure alone is175files/204753053bytes.
GPU allocation was1MiB after service release. The current source comment that
post-release analysis cannot extend GPU allocation is wrong about scheduling:
the next accepted waiter still waits for this driver and its enclosing parent.

Main will send SIGINT only to this exact owned driver, after checking the saved
terminal/hash,96 files, two service markers, empty GPU, UID/start/PGID and no
children again. No predecessor coordinator, service, model checkpoint or unrelated
process is signaled or edited. The enclosing coordinator will preserve the
nonzero exit rather than retry, release its normal lock and let grammar160 start.
If the driver has already exited, no signal is sent.

The frozen source, raw episodes, routes, usage, checkpoints and TERMINAL remain
unchanged. A missing or partial built-in analysis is not promoted as evidence.
The independent CPU audit owns subsequent score recomputation outside the GPU
schedule. Record the terminal-to-job-exit interval as avoidable CPU-tail idle,
not model inference or training time. This recovery does not make the operation
an exit0 run; distinguish completed GPU data collection from interrupted analysis.

Future operations should release GPU scheduling authority before CPU analysis
and avoid rehashing the same immutable closure inside a per-episode loop. This
decision does not hot-patch the accepted runtime or generalize cleanup authority.
