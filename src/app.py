import logging
from json import load

from dotenv import dotenv_values
from flask import Flask, Response, redirect, url_for

from .login import login
from .data import Data
from .settings import DATA_DIR, OPTIONS_DIR, STATIC_DIR
from .user import users
from .views import View
from .views.admin import admin
from .views.auth import auth
from .views.data import data
from .views.home import home
from .views.user import user


class App(Flask):
    def __init__(self) -> None:
        super().__init__(__name__)

        # ---------------------------------- Config ---------------------------------- #

        self.config.from_mapping(dotenv_values())
        self.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{users.__file__}"

        DATA_DIR.mkdir(exist_ok=True)

        logging.basicConfig(level=logging.DEBUG, filename="flask.log")

        # -------------------------------- Initialise -------------------------------- #

        login.init(self)
        users.init(self)

        # -------------------------------- Environment ------------------------------- #

        @self.context_processor
        def global_vars() -> dict:
            with (
                open(OPTIONS_DIR / "departments.json", "r") as departments_file,
                open(OPTIONS_DIR / "levels.json", "r") as levels_file,
                open(OPTIONS_DIR / "locations.json", "r") as locations,
                open(OPTIONS_DIR / "topics.json", "r") as topics_file
            ):
                return {
                    "styles": [file.name for file in STATIC_DIR.iterdir()],
                    "categories": Data.categories,
                    "departments": load(departments_file),
                    "levels": load(levels_file),
                    "locations": load(locations),
                    "topics": load(topics_file),
                }

        # -------------------------------- Blueprints -------------------------------- #

        self.register_blueprint(admin, url_prefix="/admin")
        self.register_blueprint(auth, url_prefix="/auth")
        self.register_blueprint(data, url_prefix="/data")
        self.register_blueprint(home, url_prefix="/home")
        self.register_blueprint(user, url_prefix="/user")

        # ---------------------------------- Routes ---------------------------------- #

        @self.route("/")
        @self.route("/index")
        def index() -> View:
            return redirect(url_for("home.index"))

        @self.route("/sw.js")
        def service_worker() -> View:
            return Response(status=204)
