from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.domain.exceptions import AuthenticationError
from app.routes._helpers import svc
from app.security.permissions import login_required

bp = Blueprint("auth", __name__)


@bp.get("/")
@login_required
def dashboard():
    return render_template("dashboard.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            user = svc("auth_service").login(request.form.get("username", ""),
                                             request.form.get("password", ""))
        except AuthenticationError as err:
            flash(str(err), "error")
            return render_template("login.html"), 401
        session.clear()                    # fresh session on login (prevents fixation)
        session["user_id"] = user.id
        session.permanent = True           # enables the 15-minute inactivity timeout
        return redirect(url_for("auth.dashboard"))
    return render_template("login.html")


@bp.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
