from datetime import date, datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from app.domain.exceptions import AccessDenied, DomainError
from app.routes._helpers import parse_date, parse_time, svc
from app.security.permissions import role_required
from app.services.booking_rules import SLOT_TIMES

bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@bp.get("/")
@role_required("RECEPTIONIST")
def list_all():
    return render_template("appointments/list.html", items=svc("appointment_service").list_all())


@bp.get("/new")
@role_required("RECEPTIONIST")
def new():
    service = svc("appointment_service")
    doctor_id = request.args.get("doctor_id", type=int)
    day = parse_date(request.args.get("date"))
    booked = service.booked_times(doctor_id, day) if doctor_id and day else None
    return render_template(
        "appointments/book.html", patients=svc("patient_service").list_active(),
        doctors=service.list_doctors(), doctor_id=doctor_id, day=day, booked=booked,
        slots=SLOT_TIMES, today=date.today())


@bp.post("/")
@role_required("RECEPTIONIST")
def book():
    form = request.form
    day, slot = parse_date(form.get("date")), parse_time(form.get("slot"))
    patient_id, doctor_id = form.get("patient_id", type=int), form.get("doctor_id", type=int)
    back = url_for("appointments.new", doctor_id=doctor_id, date=form.get("date"))
    if not (patient_id and doctor_id and day and slot):
        flash("Choose a patient, doctor, date and time slot.", "error")
        return redirect(back)
    try:
        svc("appointment_service").book(patient_id, doctor_id, datetime.combine(day, slot))
    except DomainError as err:
        flash(str(err), "error")
        return redirect(back)
    flash("Appointment booked.", "success")
    return redirect(url_for("appointments.list_all"))


@bp.post("/<int:appointment_id>/cancel")
@role_required("RECEPTIONIST")
def cancel(appointment_id):
    try:
        svc("appointment_service").cancel(appointment_id)
        flash("Appointment cancelled. The slot is free again.", "success")
    except DomainError as err:
        flash(str(err), "error")
    return redirect(url_for("appointments.list_all"))


@bp.get("/schedule")
@role_required("DOCTOR")
def schedule():
    # the doctor's identity comes from the SESSION, never the URL
    day = parse_date(request.args.get("date")) or date.today()
    items = svc("appointment_service").schedule_for(g.user.id, day)
    return render_template("appointments/schedule.html", items=items, day=day)


@bp.post("/<int:appointment_id>/complete")
@role_required("DOCTOR")
def complete(appointment_id):
    try:
        svc("appointment_service").mark_completed(appointment_id, g.user.id)
        flash("Appointment marked as completed.", "success")
    except AccessDenied:
        raise                      # someone else's appointment: a hard 403, not a friendly message
    except DomainError as err:
        flash(str(err), "error")
    return redirect(url_for("appointments.schedule", date=request.form.get("date", "")))
