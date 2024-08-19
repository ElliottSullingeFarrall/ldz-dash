from functools import wraps

from flask import redirect, render_template, request, url_for
from flask_login import current_user  # type: ignore
from werkzeug import Response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.admin:
            return
        return f(*args, **kwargs)
    return decorated_function

def confirm_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "GET":
            return render_template("confirm.html")
        elif request.method == "POST":
            if "confirm" in request.form:
                return f(*args, **kwargs)
    return decorated_function

View = Response | str
