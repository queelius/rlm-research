# Keep small exploratory jobs executable

Updated September 10, 2026. These are lessons from observed launch failures,
not a request for another general testing framework.

Recent jobs passed tests but failed before useful GPU work because a borrowed
module looked for configuration under the wrong directory. Examples include
missing `START.json`, missing `GATE_PLAN.json`, and a wrapper whose `PRIOR` points
back to itself when another module is loaded under a new namespace.

For the next small experiment:

- Prefer a short explicit entry point over another layer of dynamically rebound
  wrappers. Pass the model, input path, output path and deadline explicitly where
  practical. Do not refactor an active experiment to achieve this.
- A CLI help check or successful import does not exercise collection. Run one
  nonempty frozen coordinate through the actual collector with a fake local
  response before GPU launch. Exercise parsing, scoring and final status too.
- Check inherited inventory counts and required files together. A144-call study
  must not inherit a192-call terminal check or a fourth, absent comparison arm.
- Keep the correct comparison in view. Two similarly effective interfaces do
  not replace an untreated baseline when asking whether an improvement survives
  a whole task. Bind the intended model, not just a convenient service alias.
- Rebuild the meaning of each inherited condition, not just its label. The first
  balanced-tag draft dropped requested_tag but retained wrong/alien/aligned labels;
  without an actual reference those became mere unused-ID renamings. MAIN caught
  this before launch. A focused request-field and named-record diagnostic check
  is useful; no production refactor is needed.
- Preserve failed attempts, including their source revision and configuration,
  and repair the observed seam. More hashes or broad tests are not substitutes
  for exercising the actual path that failed.

Do this CPU preparation while another meaningful job uses the GPU. If no job is
running, make the smallest informative executable comparison the priority.
