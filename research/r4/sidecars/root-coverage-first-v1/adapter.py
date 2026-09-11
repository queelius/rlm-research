"""Private composition of the unchanged qualified task/native install seam."""
import study as s
import overlay
with s.aliases({'study':s,'overlay':overlay}):
    _old=s.load('coverage_original_adapter',s.OLD/'adapter.py',s.old_pins()[str(s.OLD/'adapter.py')])
environment=_old.environment
task=_old.task
installed=_old.installed
