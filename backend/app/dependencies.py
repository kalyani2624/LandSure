# Re-export for backward compatibility
from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    check_admin_role,
    get_db,
    oauth2_scheme
)
from app.core.security import verify_password, get_password_hash, create_access_token

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "check_admin_role",
    "get_db",
    "oauth2_scheme",
    "verify_password",
    "get_password_hash",
    "create_access_token"
]
