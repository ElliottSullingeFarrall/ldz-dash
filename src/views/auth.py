from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user  # type: ignore

from src.user import UserException, users

from . import View

auth = Blueprint("auth", __name__, template_folder="../templates/auth")

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
