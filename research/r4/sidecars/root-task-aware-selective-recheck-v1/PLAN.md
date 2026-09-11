# Execution plan

- Question: does local public-J1 sensitivity improve confidence targeting, and does A/B agreement
  abstention reduce harmful overwrites?
- Immutable panel: the eight frozen ceiling episodes, fixed 25% selection budget, no gold in selection
  or request bodies.
- Calls: 2 selections × 2 samples × 12 repacked requests = 48, one c32 service, four workers.
- Seeds: paired across selections by episode, sample, and repack; catalog-scanned before sealing.
- Cap: one A100, 1,200 seconds inclusive; 90-second request cap inherited from the qualified collector.
- No training, retry, reroll, answer fallback, or partial batch salvage.
- MAIN alone may launch after READY review.

