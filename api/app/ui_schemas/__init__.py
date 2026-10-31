"""Schema-driven UI: form specs built from the Pydantic models, so validation
rules live in exactly one place. The web SchemaForm renders them statically.
Add a form = add a `spec(...)` entry to a module here and import it below."""
from app.ui_schemas.base import REGISTRY, spec  # noqa: F401
from app.ui_schemas import account, admin, applications, projects  # noqa: F401,E402  (registers specs)
