"""Pinned producer scorer loaded under the replication protocol namespace."""
import study as s,protocol as p
module=s.load('field_order_replication_scoring',s.FIELD_ORDER/'scoring_v2.py','b92fa7698935be4e3b1c8d371374fe7abeee449ca5d72d684b6eaded816a6af2',{'study':s,'protocol_v2':p})
verified_response,missing,score=module.verified_response,module.missing,module.score
