"""Execute the exact frozen owned driver with the new checkpoint-only study view."""
import study as s
exec(compile(s.source('driver.py'),str(s.OLD/'driver.py')+':rl4-binding-only','exec'),globals())
