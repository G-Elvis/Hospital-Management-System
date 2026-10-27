from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from app.domain.exceptions import ValidationError
from app.routes._helpers import svc
from app.security.permissions import role_required

bp = Blueprint("records", __name__, url_prefix="/patients/<int:patient_id>/records")


@bp.get("/")
@role_required("DOCTOR")
def history(patient_id):
    patient = svc("patient_service").get(patient_id)
    return render_template("records/history.html", patient=patient,
                           entries=svc("record_service").history_for(patient_id))


@bp.route("/new", methods=["GET", "POST"])
@role_required("DOCTOR")
def add(patient_id):
    patient = svc("patient_service").get(patient_id)
    if request.method == "GET":
        return render_template("records/add.html", patient=patient, form={})
    form = request.form
    try:
        # g.user.id is the author: any "doctor_id" field in the form is ignored
        svc("record_service").add_record(g.user.id, patient_id, form.get("diagnosis", ""),
                                         form.get("treatment", ""), form.get("prescription", ""))
    except ValidationError as err:
        return render_template("records/add.html", patient=patient, form=form,
                               errors=err.errors), 400
    flash("Medical record saved.", "success")
    return redirect(url_for("records.history", patient_id=patient_id))
