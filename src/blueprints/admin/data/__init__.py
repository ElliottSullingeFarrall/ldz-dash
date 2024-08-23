from flask import Blueprint, Response, render_template, request

from src.data import Data
from src.user import users

from ...utils import View, admin_required, TEMPLATES_DIR

TEMPLATES_DIR = TEMPLATES_DIR / "admin" / "data"

data = Blueprint("data", __name__, url_prefix="/data")

@data.route("/", methods=["GET", "POST"])
@admin_required
def download() -> View:
    if request.method == "POST":
        df = Data.pull(request.form)
        return Response(df.to_csv(index=False), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=data.csv"})

    return render_template(str(TEMPLATES_DIR / "download.html"), users=users.list_view)
