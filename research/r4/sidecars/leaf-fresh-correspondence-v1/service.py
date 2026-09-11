"""Same pinned released-model service configuration, no research adapters."""
import study as s
inherited=s.private('service.py')
OLD=inherited.OLD
config,descriptor,validate_descriptor,validate_models=inherited.config,inherited.descriptor,inherited.validate_descriptor,inherited.validate_models
