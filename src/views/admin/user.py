from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
)

from .. import View, admin_required, confirm_required
from src.settings import TEMPLATES_DIR
from src.user import UserException, current_user, users

user = Blueprint("user", __name__, url_prefix="/user", template_folder=TEMPLATES_DIR / "admin"/ "user")

@user.route("/")
@admin_required
def view() -> View:
    table = users.table_view
    return render_template("view.html", headers=table.columns, table=table.values)

@user.route("/add", methods=["GET", "POST"])
@admin_required
def add() -> View:
    if request.method == "POST":
        try:
            print(request.form)
            users.append(request.form)
            print(users)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for(".view"))

    return render_template("add.html")

@user.route("/import", methods=["GET", "POST"])
@admin_required
def _import() -> View:
    if request.method == "POST":
        try:
            users.from_csv(request.files)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for(".view"))

    return render_template("import.html")

@user.route("/edit/<int:idx>", methods=["GET", "POST"])
@admin_required
def edit(idx: int) -> View:
    if request.method == "POST":
        try:
            users.reset_password(idx, request.form)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for(".view"))

    user = users[idx]
    if user == current_user:
        return redirect(url_for(".view"))

    return render_template("edit.html", idx=idx)

@user.route("/remove/<int:idx>", methods=["GET", "POST"])
@admin_required
@confirm_required
def remove(idx: int) -> View:
    del users[idx]
    return redirect(url_for(".view"))
