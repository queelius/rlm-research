"""Identical accepted raw collector with the new study endpoint binding."""
import study as s
with s.aliases({'study':s},s.PARENT):implementation=s.load('BA18_dose_same_collector',s.PARENT/'collect.py')
Collector=implementation.Collector
execute=implementation.execute
