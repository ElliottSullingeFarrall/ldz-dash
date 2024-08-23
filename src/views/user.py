from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.settings import TEMPLATES_DIR
from src.user import UserException, users

from . import View, login_required

user = Blueprint("user", __name__, template_folder=TEMPLATES_DIR / "user")

@user.route("/settings", methods=["GET", "POST"])
@login_required
def settings() -> View:
    if request.method == "POST":
        try:
            users.change_password(request.form)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for("home.index"))

    return render_template("settings.html")
