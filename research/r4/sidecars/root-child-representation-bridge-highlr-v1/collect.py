"""Exact frozen collector; only four immutable input reads target their original paths."""
import study as s
source=s.source('collect.py');before="s.ROOT/'inputs/"
if source.count(before)!=4:raise ValueError('immutable input path seam changed')
source=source.replace(before,"s.OLD/'inputs/")
with s.aliases({'adapter':s.adapter()}):exec(compile(source,str(s.OLD/'collect.py')+':highlr-binding-only','exec'),globals())
