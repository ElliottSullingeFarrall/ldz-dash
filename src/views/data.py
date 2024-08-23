from flask import Blueprint, redirect, render_template, request, url_for

from src.data import Data
from src.settings import TEMPLATES_DIR

from . import View, confirm_required, login_required

data = Blueprint("data", __name__, url_prefix="/data", template_folder=TEMPLATES_DIR / "data")

@data.route("/<category>/<type>", methods=["GET", "POST"])
@login_required
def add(category: str, type: str) -> View:
    if request.method == "POST":
        with Data(category, type) as data:
            data.append(request.form)
        return redirect(url_for(".add", category=category, type=type))

    return render_template(f"{category}/{type}.html", category=category, type=type)

@data.route("/<category>/<type>/view")
@login_required
def edit(category: str, type: str) -> View:
    with Data(category, type) as data:
        return render_template("edit.html", category=category, type=type, headers=data.df.columns, table=data.df.values)

@data.route("/<category>/<type>/remove/<int:idx>", methods=["GET", "POST"])
@login_required
@confirm_required
def remove(category: str, type: str, idx: int) -> View:
    with Data(category, type) as data:
        del data[idx]
    return redirect(url_for(".edit", category=category, type=type))
