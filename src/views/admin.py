from flask import (
    Blueprint, Response, flash, redirect, render_template, request, url_for,
)
from flask_login import current_user  # type: ignore

from src.data import Data
from src.user import UserException, users

from . import View, admin_required, confirm_required

admin = Blueprint("admin", __name__, template_folder="../templates/admin")

# ----------------------------------- User ----------------------------------- #

@admin.route("/user")
@admin_required
def user_view() -> View:
    table = users.table_view
    return render_template("user/view.html", headers=table.columns, table=table.values)

@admin.route("/user/add", methods=["GET", "POST"])
@admin_required
def user_add() -> View:
    if request.method == "POST":
        try:
            print(request.form)
            users.append(request.form)
            print(users)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for(".user_view"))

    return render_template("user/add.html")

@admin.route("/user/import", methods=["GET", "POST"])
@admin_required
def user_import() -> View:
    if request.method == "POST":
        try:
            users.from_csv(request.files)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for(".user_view"))

    return render_template("user/import.html")

@admin.route("/user/edit/<int:idx>", methods=["GET", "POST"])
@admin_required
def user_edit(idx: int) -> View:
    if request.method == "POST":
        try:
            users.reset_password(idx, request.form)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for(".user_view"))

    user = users[idx]
    if user == current_user:
        return redirect(url_for(".user_view"))

    return render_template("user/edit.html", idx=idx)

@admin.route("/user/remove/<int:idx>", methods=["GET", "POST"])
@admin_required
@confirm_required
def user_remove(idx: int) -> View:
    del users[idx]
    return redirect(url_for(".user_view"))

# ----------------------------------- Data ----------------------------------- #

@admin.route("/data", methods=["GET", "POST"])
@admin_required
def data() -> View:
    if request.method == "POST":
        df = Data.pull(request.form)
        return Response(df.to_csv(index=False), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=data.csv"})

    return render_template("data.html", users=users.list_view)
