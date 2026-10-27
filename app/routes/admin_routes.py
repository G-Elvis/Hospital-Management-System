from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.domain.exceptions import DomainError, ValidationError
from app.domain.user import Role
from app.routes._helpers import svc
from app.security.permissions import role_required

bp = Blueprint("admin", __name__, url_prefix="/admin/users")


@bp.get("/")
@role_required("ADMIN")
def users():
    return render_template("admin/users.html", users=svc("admin_service").list_users(),
                           roles=[r.value for r in Role], form={})


@bp.post("/")
@role_required("ADMIN")
def create():
    form = request.form
    try:
        svc("admin_service").create_user(form.get("username", ""), form.get("password", ""),
                                         form.get("role", ""))
    except ValidationError as err:
        return render_template("admin/users.html", users=svc("admin_service").list_users(),
                               roles=[r.value for r in Role], form=form,
                               errors=err.errors), 400
    except DomainError as err:
        flash(str(err), "error")
        return redirect(url_for("admin.users"))
    flash("User account created.", "success")
    return redirect(url_for("admin.users"))


@bp.post("/<int:user_id>/deactivate")
@role_required("ADMIN")
def deactivate(user_id):
    try:
        svc("admin_service").deactivate(user_id)
        flash("Account deactivated.", "success")
    except DomainError as err:
        flash(str(err), "error")
    return redirect(url_for("admin.users"))


@bp.post("/<int:user_id>/role")
@role_required("ADMIN")
def change_role(user_id):
    try:
        svc("admin_service").change_role(user_id, request.form.get("role", ""))
        flash("Role updated. It applies on the user's next request.", "success")
    except DomainError as err:
        flash(str(err), "error")
    return redirect(url_for("admin.users"))
