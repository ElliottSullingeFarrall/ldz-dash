import logging
from json import load
from pathlib import Path

from dotenv import dotenv_values  # type: ignore
from flask import Flask, Response, redirect, url_for

from .auth import auth
from .data import Data
from .user import users
from .views import View
from .views.admin import admin as admin_blueprint
from .views.auth import auth as auth_blueprint
from .views.data import data as data_blueprint
from .views.home import home as home_blueprint
from .views.user import user as user_blueprint


class App(Flask):
    def __init__(self) -> None:
        super().__init__(__name__)

        # ---------------------------------- Config ---------------------------------- #

        self.config.from_mapping(dotenv_values())
        self.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{users.__file__}"

        Data.data_dir.mkdir(exist_ok=True)

        logging.basicConfig(level=logging.DEBUG, filename="flask.log")

        # -------------------------------- Initialise -------------------------------- #

        auth.init(self)
        users.init(self)

        # -------------------------------- Environment ------------------------------- #

        @self.context_processor
        def global_vars() -> dict:
            options_dir = Path(__file__).parent / "options"
            static_dir = Path(__file__).parent / "static"
            with (
                open(options_dir / "departments.json", "r") as departments_file,
                open(options_dir / "levels.json", "r") as levels_file,
                open(options_dir / "locations.json", "r") as locations,
                open(options_dir / "topics.json", "r") as topics_file
            ):
                return {
                    "styles": [file.name for file in static_dir.iterdir()],
                    "categories": Data.categories,
                    "departments": load(departments_file),
                    "levels": load(levels_file),
                    "locations": load(locations),
                    "topics": load(topics_file),
                }

        # -------------------------------- Blueprints -------------------------------- #

        self.register_blueprint(admin_blueprint, url_prefix="/admin")
        self.register_blueprint(auth_blueprint, url_prefix="/auth")
        self.register_blueprint(data_blueprint, url_prefix="/data")
        self.register_blueprint(home_blueprint, url_prefix="/home")
        self.register_blueprint(user_blueprint, url_prefix="/user")

        # ---------------------------------- Routes ---------------------------------- #

        @self.route("/")
        @self.route("/index")
        def index() -> View:
            return redirect(url_for("home.index"))

        @self.route("/sw.js")
        def service_worker() -> View:
            return Response(status=204)
