from pathlib import Path

from dotenv import dotenv_values
from flask import Blueprint, Response, abort, request
from git import Repo

from . import View

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/update", methods=["POST"])
def update() -> View:
    secret_key = dotenv_values()["SECRET_KEY"]
    request_key = request.headers.get("X-Secret-Key")
    wsgi_file = request.headers.get("X-WSGI-File")

    if secret_key is not request_key:
        abort(403)

    if request.method == "POST":
        repo = Repo()
        repo.remotes.origin.pull()

        with open("VERSION", "w") as version_file:
            version_file.write(repo.head.object.hexsha)

        if wsgi_file:
            Path(wsgi_file).touch()
            return Response(status=200)
        else:
            return Response(status=202)
    else:
        return Response(status=400)

@api.route("/version")
def version() -> View:
    if Path("VERSION").exists():
        with open("VERSION", "r") as version_file:
            return version_file.read()
    else:
        abort(404)
