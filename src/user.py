from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from flask_login import (  # type: ignore
    UserMixin, current_user, login_user, logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from pandas import DataFrame, read_csv, read_sql
from werkzeug.security import check_password_hash, generate_password_hash

from .data import Data


class Users(SQLAlchemy):
    __file__ = Path(__file__).parent.parent / "data" / "users.sqlite"

    def init(self, app) -> None:
        self.init_app(app)
        with app.app_context():
            self.create_all()
            if self.empty:
                self.append({"username": "default", "password": "default", "admin": True})

    def append(self, form: dict) -> None:
        user = User.query.filter_by(username=form["username"]).first()

        if not user:
            user = User(username=form["username"], password=generate_password_hash(form["password"]), admin=bool(form.get("admin")))
            self.session.add(user)
            self.session.commit()
        else:
            raise UserException("User already exists!")

    def __getitem__(self, idx: int) -> "User":
        table = read_sql(User.query.statement, self.engine)
        user = User.query.filter_by(username=table.at[idx, "username"]).first()

        if not user:
            raise UserException("Invalid user!")
        return user

    def __delitem__(self, idx: int) -> None:
        table = read_sql(User.query.statement, self.engine)
        user = User.query.filter_by(username=table.at[idx, "username"]).first()

        if not user:
            raise UserException("Invalid user!")

        self.session.delete(user)
        self.session.commit()

        user_data = Data.data_dir / user.username
        if user_data.exists():
            rmtree(user_data)

    def __len__(self) -> int:
        return User.query.count()

    @property
    def empty(self) -> bool:
        return not len(self)

    # ------------------------------ User Management ----------------------------- #

    def login(self, form: dict) -> None:
        user = User.query.filter_by(username=form["username"]).first()
        if not user:
            raise UserException("Invalid user!")

        if not check_password_hash(user.password, form["password"]):
            raise UserException("Invalid password!")

        login_user(user)

    def logout(self) -> None:
        logout_user()

    def change_password(self, form: dict) -> None:
        user = User.query.filter_by(username=current_user.username).first()
        if not user:
            raise UserException("Invalid user!")

        if form["password_new"] is not form["password_check"]:
            raise UserException("Passwords do not match!")
        if not check_password_hash(user.password, form["password_old"]):
            raise UserException("Invalid password!")

        user.password = generate_password_hash(form["password_new"])
        self.session.commit()

    def reset_password(self, idx: int, form: dict) -> None:
        table = read_sql(User.query.statement, users.engine)
        user = User.query.filter_by(username=table.at[idx, "username"]).first()
        if not user:
            raise UserException("Invalid user!")

        if form["password_new"] is not form["password_check"]:
            raise UserException("Passwords do not match!")

        user.password = generate_password_hash(form["password_new"])
        self.session.commit()

    # ------------------------------ Import / Export ----------------------------- #

    @property
    def list_view(self) -> dict:
        users = dict.fromkeys([user.username for user in User.query.all()])
        for username in users:
            last_submission = None

            for category in Data.categories:
                for type in Data.categories[category]:
                    with Data(category, type, username) as data:
                        if "Date" not in data.df:
                            continue

                        if not last_submission:
                            last_submission = data.df["Date"].max()
                        else:
                            last_submission = max(last_submission, data.df["Date"].max())
            users[username] = last_submission

        return users

    @property
    def table_view(self) -> DataFrame:
        table = read_sql(User.query.statement, users.engine)

        table.pop("id")
        table.pop("password")

        return table

    def from_csv(self, files: dict) -> None:
        file = files["users"]

        if file.filename == "":
            raise UserException("No selected file!")
        if not file.filename.endswith(".csv"):
            raise UserException("Invalid file type!")

        with NamedTemporaryFile(suffix=".csv") as temp:
            file.save(temp.name)
            df = read_csv(temp.name)

        for _, row in df.iterrows():
            user = User.query.filter_by(username=row["username"]).first()
            if not user:
                self.append(row.to_dict())
            else:
                raise UserException("User already exists!")

users = Users()

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model
else:
    Model = users.Model

@dataclass
class User(Model, UserMixin):
    id: int = users.Column(users.Integer, primary_key=True)
    username: str = users.Column(users.String(100), nullable=False, unique=True)
    password: str = users.Column(users.String(100), nullable=False)
    admin: bool = users.Column(users.Boolean, nullable=False, default=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self.username == other.username

class UserException(Exception):
    def __init__(self, message: str = "Unknown error!") -> None:
        self.message = message
        super().__init__(message)
