from flask import Blueprint

from .data import data
from .user import user

from ..utils import TEMPLATES_DIR

TEMPLATES_DIR = TEMPLATES_DIR / "admin"

admin = Blueprint("admin", __name__, url_prefix="/admin")

admin.register_blueprint(data)
admin.register_blueprint(user)
