"""JSON API used by the Vue front end (frontend/)."""
from datetime import datetime

from flask import Blueprint, current_app, g, jsonify, request, session

from app.domain.exceptions import (AccessDenied, AuthenticationError, DomainError, NotFound,
                                   PossibleDuplicate, ValidationError)
from app.domain.user import Role
from app.routes._helpers import parse_date, parse_time, svc
from app.security.csrf import _token
from app.security.permissions import role_required
from app.services.booking_rules import SLOT_TIMES
from app.validators.patient_validator import GENDERS

bp = Blueprint("api", __name__, url_prefix="/api")


# ---- serialisers -----------------------------------------------------------
def _user(user):
    return {"id": user.id, "username": user.username, "role": user.role.value}


def _patient(p):
    return {"id": p.id, "full_name": p.full_name, "date_of_birth": p.date_of_birth.isoformat(),
            "gender": p.gender, "phone": p.phone, "address": p.address}


def _appointment(view):
    a = view.appointment
    return {"id": a.id, "patient_id": a.patient_id, "patient_name": view.patient_name,
            "doctor_id": a.doctor_id, "doctor_name": view.doctor_name,
            "start_time": a.start_time.isoformat(timespec="minutes"), "status": a.status.value}


def _record(entry):
    r = entry.record
    return {"id": r.id, "created_at": r.created_at.isoformat(timespec="minutes"),
            "doctor_name": entry.doctor_name, "diagnosis": r.diagnosis,
            "treatment": r.treatment, "prescription": r.prescription}


def _session_payload():
    return {"user": _user(g.user) if g.user else None, "csrf_token": _token(),
            "session_lifetime": int(
                current_app.config["PERMANENT_SESSION_LIFETIME"].total_seconds())}


# ---- errors are returned as JSON, never as redirects or HTML ---------------
@bp.errorhandler(401)
def _unauthorised(_):
    return jsonify(error="Please log in to continue."), 401


@bp.errorhandler(400)
def _bad_request(_):
    return jsonify(error="The session expired or the request was invalid. Reload and try again."
                   ), 400


@bp.errorhandler(403)
@bp.errorhandler(AccessDenied)
def _forbidden(_):
    return jsonify(error="Your role does not allow this action."), 403


@bp.errorhandler(404)
@bp.errorhandler(NotFound)
def _not_found(err):
    message = str(err) if isinstance(err, NotFound) else "We could not find what you asked for."
    return jsonify(error=message), 404


@bp.errorhandler(ValidationError)
def _invalid(err):
    return jsonify(error=str(err), errors=err.errors), 400


@bp.errorhandler(PossibleDuplicate)
def _duplicate(err):
    return jsonify(error=str(err)), 409


@bp.errorhandler(DomainError)
def _domain_error(err):
    return jsonify(error=str(err)), 409


# ---- session ---------------------------------------------------------------
@bp.get("/session")
def current_session():
    return jsonify(_session_payload())


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    try:
        user = svc("auth_service").login(str(data.get("username", "")),
                                         str(data.get("password", "")))
    except AuthenticationError as err:
        return jsonify(error=str(err)), 401
    session.clear()                        # fresh session on login (prevents fixation)
    session["user_id"] = user.id
    session.permanent = True               # enables the 15-minute inactivity timeout
    g.user = user
    return jsonify(_session_payload())


@bp.post("/logout")
def logout():
    session.clear()
    g.user = None
    return jsonify(_session_payload())


# ---- reference data --------------------------------------------------------
@bp.get("/slots")
@role_required("RECEPTIONIST", "DOCTOR")
def slots():
    return jsonify(slots=[t.strftime("%H:%M") for t in SLOT_TIMES])


@bp.get("/genders")
@role_required("RECEPTIONIST", "DOCTOR")
def genders():
    return jsonify(genders=list(GENDERS))


@bp.get("/doctors")
@role_required("RECEPTIONIST", "DOCTOR")
def doctors():
    return jsonify(doctors=[{"id": d.id, "username": d.username}
                            for d in svc("appointment_service").list_doctors()])


# ---- patients --------------------------------------------------------------
@bp.get("/patients")
@role_required("RECEPTIONIST", "DOCTOR")
def patients():
    found = svc("patient_service").search(request.args.get("q", ""))
    return jsonify(patients=[_patient(p) for p in found])


@bp.post("/patients")
@role_required("RECEPTIONIST")
def register_patient():
    data = request.get_json(silent=True) or {}
    created = svc("patient_service").register(
        str(data.get("full_name", "")), parse_date(data.get("date_of_birth")),
        str(data.get("gender", "")), str(data.get("phone", "")), str(data.get("address", "")),
        confirm_duplicate=data.get("confirm_duplicate") is True)
    return jsonify(patient=_patient(created)), 201


@bp.get("/patients/<int:patient_id>")
@role_required("RECEPTIONIST", "DOCTOR")
def patient(patient_id):
    return jsonify(patient=_patient(svc("patient_service").get(patient_id)))


# ---- appointments ----------------------------------------------------------
@bp.get("/appointments")
@role_required("RECEPTIONIST", "DOCTOR")
def appointments():
    items = svc("appointment_service").list_all()
    if g.user.role == Role.DOCTOR:         # a doctor only ever sees their own appointments
        items = [v for v in items if v.appointment.doctor_id == g.user.id]
    return jsonify(appointments=[_appointment(v) for v in items])


@bp.post("/appointments")
@role_required("RECEPTIONIST")
def book():
    data = request.get_json(silent=True) or {}
    day, slot = parse_date(data.get("date")), parse_time(data.get("slot"))
    patient_id, doctor_id = data.get("patient_id"), data.get("doctor_id")
    if not (isinstance(patient_id, int) and isinstance(doctor_id, int) and day and slot):
        return jsonify(error="Choose a patient, doctor, date and time slot."), 400
    created = svc("appointment_service").book(patient_id, doctor_id, datetime.combine(day, slot))
    return jsonify(appointment_id=created.id), 201


@bp.post("/appointments/<int:appointment_id>/cancel")
@role_required("RECEPTIONIST")
def cancel(appointment_id):
    svc("appointment_service").cancel(appointment_id)
    return jsonify(ok=True)


@bp.post("/appointments/<int:appointment_id>/complete")
@role_required("DOCTOR")
def complete(appointment_id):
    svc("appointment_service").mark_completed(appointment_id, g.user.id)
    return jsonify(ok=True)


# ---- medical records -------------------------------------------------------
@bp.get("/patients/<int:patient_id>/records")
@role_required("DOCTOR")
def records(patient_id):
    entries = svc("record_service").history_for(patient_id)
    return jsonify(records=[_record(e) for e in entries])


@bp.post("/patients/<int:patient_id>/records")
@role_required("DOCTOR")
def add_record(patient_id):
    data = request.get_json(silent=True) or {}
    # g.user.id is the author: any "doctor_id" in the body is ignored
    svc("record_service").add_record(g.user.id, patient_id, str(data.get("diagnosis", "")),
                                     str(data.get("treatment", "")),
                                     str(data.get("prescription", "")))
    return jsonify(ok=True), 201
