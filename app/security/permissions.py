"""One reusable decorator enforces role-based access on every route (FR-AUTH-04/05)."""
from functools import wraps

from flask import abort, g

from app.domain.user import Role


def role_required(*roles):
    allowed = {Role(r) for r in roles}

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if g.get("user") is None:
                abort(401)                  # not logged in
            if g.user.role not in allowed:
                abort(403)                  # logged in, but the wrong role
            return view(*args, **kwargs)
        return wrapper
    return decorator


def login_required(view):
    """Any logged-in user, whatever their role."""
    return role_required(*Role)(view)
