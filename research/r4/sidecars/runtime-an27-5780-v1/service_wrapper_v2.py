"""Report actual wrapper hash to the symmetrically adapted ownership verifier."""
from pathlib import Path
import sys
from types import ModuleType
import service_wrapper as driver
import lifecycle_adapter as lifecycle

def main():
    lifecycle.verify()
    driver.runtime.verify_runtime()
    if not Path(driver.DRIVER).is_dir():
        raise ValueError('actual allocation driver missing')
    sys.path.insert(0, str(driver.SOURCE.parent))
    module = ModuleType('allocation5780_pinned_service_v2')
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__.update(adapt_environment=driver.adapt_environment,
        runtime_wrapper_sha=driver.runtime.sha(Path(__file__)))
    exec(compile(driver.source_text(), str(driver.SOURCE) + ':allocation-driver-actual-identity', 'exec'), module.__dict__)
    module.main()

if __name__ == '__main__':
    main()
