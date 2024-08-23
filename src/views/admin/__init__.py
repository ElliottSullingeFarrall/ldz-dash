from flask import Blueprint

from .data import data
from .user import user

admin = Blueprint("admin", __name__)

admin.register_blueprint(data, url_prefix="/data")
admin.register_blueprint(user, url_prefix="/user")
