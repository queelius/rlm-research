# One additive offline native fixture

September 9, 2026. Main read the complete attempt-002 fixture source, recorded
fixture-02 failure and fixture-01 comparison. The first native fixture matched
all three historical prompt/sampling/alias records. The second failed when a
locally authored shell script was passed as str to DockerRuntime.write, before
the offline check; this does not establish a failure of the installed image.

Authorize one new 180-second CPU fixture against the already built private image,
with the script encoded to bytes and the same scoped offline canary/check enabled.
Use a new fixture output and additive source; preserve both old fixtures and the
old source. No image rebuild, GPU/model calls, source-policy changes, shared-store
writes or changing the accepted GPU jobs. Count this as a third qualification
attempt, not a successful retry of the second. Verify the bytes boundary with a
focused fake-runtime check before the fresh container. Report actual partial
success or failure; scoped command denial is not a general network sandbox.
