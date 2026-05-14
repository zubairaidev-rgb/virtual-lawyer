"""
Application startup hook for database readiness.

Called from ``api_complete`` during import: ensures indexes exist and runs a
minimal seed when collections are empty (see ``db.seed``).
"""
from .repository import init_schema
from .seed import seed_if_empty


def init_app_database() -> None:
    """Create indexes and seed default admin/settings if needed."""
    init_schema()
    seed_if_empty()
    print("Database ready (MongoDB)")
