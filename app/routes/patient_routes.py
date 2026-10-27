from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.domain.exceptions import PossibleDuplicate, ValidationError
from app.routes._helpers import parse_date, svc
from app.security.permissions import role_required
from app.validators.patient_validator import GENDERS

bp = Blueprint("patients", __name__, url_prefix="/patients")


@bp.get("/")
@role_required("RECEPTIONIST", "DOCTOR")
def search():
    query = request.args.get("q", "")
    return render_template("patients/search.html", patients=svc("patient_service").search(query),
                           query=query)


@bp.route("/new", methods=["GET", "POST"])
@role_required("RECEPTIONIST")
def register():
    if request.method == "GET":
        return render_template("patients/register.html", form={}, genders=GENDERS)

    form = request.form
    try:
        patient = svc("patient_service").register(
            form.get("full_name", ""), parse_date(form.get("date_of_birth")),
            form.get("gender", ""), form.get("phone", ""), form.get("address", ""),
            confirm_duplicate=form.get("confirm_duplicate") == "yes")
    except ValidationError as err:
        return render_template("patients/register.html", form=form, genders=GENDERS,
                               errors=err.errors), 400
    except PossibleDuplicate as err:
        return render_template("patients/register.html", form=form, genders=GENDERS,
                               duplicate=str(err)), 409
    flash(f"Patient registered with ID {patient.id}.", "success")
    return redirect(url_for("patients.profile", patient_id=patient.id))


@bp.get("/<int:patient_id>")
@role_required("RECEPTIONIST", "DOCTOR")
def profile(patient_id):
    patient = svc("patient_service").get(patient_id)
    history = svc("appointment_service").history_for_patient(patient_id)
    return render_template("patients/profile.html", patient=patient, appointments=history)


@bp.post("/<int:patient_id>/edit")
@role_required("RECEPTIONIST")
def edit(patient_id):
    try:
        svc("patient_service").update_contact(
            patient_id, request.form.get("phone", ""), request.form.get("address", ""))
        flash("Patient details updated.", "success")
    except ValidationError as err:
        for message in err.errors:
            flash(message, "error")
    return redirect(url_for("patients.profile", patient_id=patient_id))


@bp.post("/<int:patient_id>/deactivate")
@role_required("RECEPTIONIST")
def deactivate(patient_id):
    svc("patient_service").deactivate(patient_id)
    flash("Patient deactivated. Their history is kept.", "success")
    return redirect(url_for("patients.search"))
