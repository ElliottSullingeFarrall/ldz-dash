from flask import (
    Blueprint, Response, render_template, request,
)

from src.data import Data
from src.settings import TEMPLATES_DIR
from src.user import users

from .. import View, admin_required

data = Blueprint("data", __name__, template_folder=TEMPLATES_DIR / "admin" / "data")

@data.route("/", methods=["GET", "POST"])
@admin_required
def download() -> View:
    if request.method == "POST":
        df = Data.pull(request.form)
        return Response(df.to_csv(index=False), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=data.csv"})

    return render_template("download.html", users=users.list_view)
