"""Same qualified engine/supervisor patches, new owned ledger payload only."""
import study as s
_old=s.load('coverage_original_overlay',s.OLD/'overlay.py',s.old_pins()[str(s.OLD/'overlay.py')])
_old.ROOT=s.ROOT
program=_old.program
SUPERVISOR=_old.SUPERVISOR
