"""Pinned adaptive owned driver with only exact count/cap updates."""
import hashlib
from pathlib import Path
import experiment as e

SOURCE=e.PRIOR/'driver.py'
SOURCE_SHA='b129d5133acd2358dd21e6fe1d3e08360a0e7c40ab353308fee191afe26e72c0'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('adaptive driver changed')
ADAPTED=SOURCE.read_text()
EDITS=[('2580','1680',2),('2700','1800',1),('2280','1440',3),
       ("'physical_planned':40,'logical_cells':48","'physical_planned':24,'logical_cells':32",1),
       ("status['recorded']!=40","status['recorded']!=24",1)]
for before,after,count in EDITS:
    if ADAPTED.count(before)!=count:raise ValueError('driver adapter seam ambiguous: '+before)
    ADAPTED=ADAPTED.replace(before,after)
exec(compile(ADAPTED,str(SOURCE)+':typed-operator-caps','exec'),globals())
