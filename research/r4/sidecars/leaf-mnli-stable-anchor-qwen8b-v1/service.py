"""Qualified released-base service config rebound to the cached 8B checkpoint."""
import study as s

module = s.load("qwen8b_stable_qualified_service", s.FREE / "service.py",
    "51215324f767d3b7fc214bed4c64e61592fb3be8223c8d5f1dd4773fae4c48cd",
    {"study": s})
config, descriptor = module.config, module.descriptor
validate_descriptor, validate_models = module.validate_descriptor, module.validate_models
OLD = module.OLD
