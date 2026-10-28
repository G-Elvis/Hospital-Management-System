import os
import sqlite3
from datetime import timedelta
from pathlib import Path

from flask import Flask, g, jsonify, redirect, render_template, request, session
from jinja2 import TemplateNotFound

from app.cli import register_cli
from app.domain.exceptions import AccessDenied, NotFound
from app.repositories.appointment_repo import SqliteAppointmentRepo
from app.repositories.patient_repo import SqlitePatientRepo
from app.repositories.record_repo import SqliteRecordRepo
from app.repositories.user_repo import SqliteUserRepo
from app.routes import (admin_routes, api_routes, appointment_routes, auth_routes,
                        patient_routes, record_routes, spa_routes)
from app.security.csrf import init_csrf
from app.security.password_hasher import WerkzeugPasswordHasher
from app.services.admin_service import AdminService
from app.services.appointment_service import AppointmentService
from app.services.auth_service import AuthService
from app.services.booking_rules import (DoctorExistsRule, NoDoctorConflictRule, NoSundayRule,
                                        NotInPastRule, PatientExistsRule, ValidSlotRule)
from app.services.patient_service import PatientService
from app.services.record_service import RecordService
from app.validators.patient_validator import PatientValidator
from app.validators.record_validator import RecordValidator


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.environ.get("DATABASE", "hms.db"),
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=15),   # FR-AUTH-07
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        CSRF_ENABLED=True,
    )
    if config:
        app.config.update(config)

    # ---- infrastructure ----------------------------------------------------
    conn = sqlite3.connect(app.config["DATABASE"], check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript((Path(__file__).parent / "schema.sql").read_text())
    app.extensions["db"] = conn

    user_repo = SqliteUserRepo(conn)
    patient_repo = SqlitePatientRepo(conn)
    appointment_repo = SqliteAppointmentRepo(conn)
    record_repo = SqliteRecordRepo(conn)
    hasher = WerkzeugPasswordHasher()

    # ---- services (dependencies are injected) ------------------------------
    app.extensions["auth_service"] = AuthService(user_repo, hasher)
    app.extensions["admin_service"] = AdminService(user_repo, hasher)
    app.extensions["patient_service"] = PatientService(patient_repo, PatientValidator())
    app.extensions["appointment_service"] = AppointmentService(
        appointment_repo,
        rules=[NotInPastRule(), ValidSlotRule(), NoSundayRule(),
               PatientExistsRule(patient_repo), DoctorExistsRule(user_repo),
               NoDoctorConflictRule(appointment_repo)],
        patients=patient_repo, users=user_repo)
    app.extensions["record_service"] = RecordService(
        record_repo, patient_repo, user_repo, RecordValidator())

    # ---- web layer ---------------------------------------------------------
    init_csrf(app)

    @app.before_request
    def load_user():
        """Look the user up on EVERY request, so deactivation/role changes apply at once."""
        g.user = None
        user_id = session.get("user_id")
        if user_id is not None:
            user = app.extensions["auth_service"].get_user(user_id)
            if user is not None and user.active:
                g.user = user
            else:
                session.clear()

    for module in (auth_routes, patient_routes, appointment_routes, record_routes,
                   admin_routes, api_routes, spa_routes):
        app.register_blueprint(module.bp)

    @app.after_request
    def security_headers(response):
        """Browser-side protections. The CSP also guarantees no inline scripts or styles run."""
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        # The Vue front end loads its fonts from Google Fonts; nothing else is relaxed.
        in_spa = request.path == "/app" or request.path.startswith("/app/")
        style_src = "'self' https://fonts.googleapis.com" if in_spa else "'self'"
        font_src = "'self' https://fonts.gstatic.com" if in_spa else "'self'"
        response.headers.setdefault(
            "Content-Security-Policy",
            f"default-src 'self'; script-src 'self'; style-src {style_src}; "
            f"font-src {font_src}; img-src 'self'; "
            "form-action 'self'; frame-ancestors 'none'; base-uri 'self'")
        if request.endpoint != "static":        # never cache pages that may show patient data
            response.headers.setdefault("Cache-Control", "no-store")
        return response

    # Templates link only to pages that exist, so the app works after every merge.
    app.jinja_env.globals["has_endpoint"] = lambda name: name in app.view_functions

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    @app.errorhandler(401)
    def unauthorised(_):
        return redirect("/app/login")           # the Vue front end owns the login screen

    def error_page(code: int, title: str, message: str):
        """JSON for /api (even for URLs no route matched), an HTML page for everything else."""
        if request.path.startswith("/api/"):
            return jsonify(error=message), code
        try:
            return render_template("error.html", code=code, title=title, message=message), code
        except TemplateNotFound:              # never let a missing template turn a 4xx into a 500
            return f"{code} {title}. {message}", code

    @app.errorhandler(400)
    def bad_request(_):
        return error_page(400, "Invalid request",
                          "The form expired or was invalid. Go back and try again.")

    @app.errorhandler(403)
    @app.errorhandler(AccessDenied)
    def forbidden(_):
        return error_page(403, "Access denied", "Your role does not allow this action.")

    @app.errorhandler(404)
    @app.errorhandler(NotFound)
    def not_found(_):
        return error_page(404, "Not found", "We could not find what you asked for.")

    @app.errorhandler(405)
    def not_allowed(_):
        return error_page(405, "Not allowed", "That action is not supported.")

    register_cli(app)
    return app
