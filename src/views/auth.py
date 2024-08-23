from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.settings import TEMPLATES_DIR
from src.user import UserException, current_user, users

from . import View

auth = Blueprint("auth", __name__, template_folder=TEMPLATES_DIR / "auth")

@auth.route("/login", methods=["GET", "POST"])
def login() -> View:
    if current_user:
        users.logout()

    if request.method == "POST":
        try:
            users.login(request.form)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for("home.index"))

    return render_template("login.html")
