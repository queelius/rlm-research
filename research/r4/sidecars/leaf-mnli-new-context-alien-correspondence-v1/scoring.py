"""Pinned exact producer scorer under the local three-arm protocol."""
import study as s,protocol as p
module=s.load('new_context_alien_exact_scoring',s.SOURCE/'scoring.py','a0f28f9c4c7e337ec1586343790468a6ea4d5bb670e6e3c54725e16d35d0b596',{'study':s,'protocol':p})
missing,score,verified_response=module.missing,module.score,module.verified_response
