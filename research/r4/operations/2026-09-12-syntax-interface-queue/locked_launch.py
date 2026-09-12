"""Retry only the pre-service orchestration, preserving the failed initial receipt."""

import run

if __name__ == "__main__":
    if (run.SIDE / "outputs/attempt-001").exists():
        raise ValueError("scientific attempt already exists")
    original = run.ROOT
    run.driver.ROOT = original / "locked-launch"
    run.driver.ROOT.mkdir(exist_ok=False)
    run.driver.write_once("LAUNCH_CONTEXT.json", {
        "authority": "MAIN", "admission": str(original / "ADMISSION.json"),
        "admission_sha256": run.driver.sha(original / "ADMISSION.json"),
        "initial_failure": "Driver correctly refused busy GPU before any service or scientific output; initial invocation omitted the external flock.",
        "resolution": "This invocation is started under external bounded shared flock; no model retry or source change.",
    })
    run.driver.main()
