"""Minimal CSRF protection: every POST must carry the secret token from the session."""
import hmac
import secrets

from flask import abort, request, session


def _token() -> str:
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]


def init_csrf(app):
    app.jinja_env.globals["csrf_token"] = _token

    @app.before_request
    def check_csrf():
        if not app.config.get("CSRF_ENABLED", True):
            return
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # HTML forms send a hidden field; the Vue front end sends a header
            sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token", "")
            expected = session.get("csrf_token", "")
            if not expected or not hmac.compare_digest(sent, expected):
                abort(400)
