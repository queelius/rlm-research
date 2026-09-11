"""Qualified actual collector, exact48/model cardinality only."""
import study as s
import service
inherited=s.private('driver.py',{'planned=72':('planned=48',1),'len(records)==72':('len(records)==48',1)},extra={'service':service})
typed_ids,verify,wire_hook,run=inherited.typed_ids,inherited.verify,inherited.wire_hook,inherited.run
if __name__=='__main__':inherited.main()
