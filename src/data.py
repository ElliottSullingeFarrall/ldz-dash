from __future__ import annotations

from flask_login import current_user # type: ignore

from calendar import month_abbr
from datetime import datetime
from html import unescape
from types import TracebackType
from typing import Optional

from pandas import DataFrame, concat, read_csv, to_datetime
from pandas.errors import EmptyDataError

from .settings import DATA_DIR, TEMPLATES_DIR


class Data:
    categories = {
        category.name: [path.stem for path in category.iterdir()]
        for category in (TEMPLATES_DIR / "data").iterdir()
        if category.is_dir()
    }

    def __init__(self, category: str, type: str, username: Optional[str] = None) -> None:
        self.category = category
        self.type = type

        if username:
            self.username = username

        else:
            self.username = current_user.username

        self.path = (DATA_DIR / self.username / category / unescape(type)).with_suffix(".csv")

    def __enter__(self) -> Data:
        if self.path.exists():
            try:
                self.df = read_csv(self.path, index_col=False)
            except EmptyDataError:
                self.df = DataFrame()
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.df = DataFrame()
        return self

    def __exit__(self, exception_type: Optional[type[BaseException]], exception_value: Optional[BaseException], exception_traceback: Optional[TracebackType]) -> None:
        self.df.to_csv(self.path, index=False)
        del self

    def append(self, row: dict) -> None:
        self.df = concat([DataFrame(row, index=[0]), self.df], ignore_index=True)
        self.df.sort_values("Date", ascending=False, inplace=True)

    def __delitem__(self, idx: int) -> None:
        self.df = self.df.drop(idx)
        self.df.sort_values("Date", ascending=False, inplace=True)

    @classmethod
    def pull(cls, form: dict) -> DataFrame:
        # For exporting user data
        dt = datetime.strptime(form["month"], "%Y-%m")
        category, type = form["category:type"].split(":")
        users = form.getlist("users") # type: ignore

        df = DataFrame()
        for user in users:
            with cls(category, type, user) as data:
                df = concat([df, data.df])

        if "Date" in df:
            df["Date"] = to_datetime(df["Date"])
            df = df.loc[(df["Date"].dt.month == dt.month) & (df["Date"].dt.year == dt.year)]
            df.sort_values("Date", ascending=False, inplace=True)

        return df

    def summarise(self, year: int) -> dict:
        # For using data in charts
        data = dict.fromkeys(month_abbr[1:], 0)

        if not self.df.empty:
            df = self.df.copy()

            df["Date"] = to_datetime(df["Date"])
            df = df[df["Date"].dt.year == year]

            for month in data:
                data[month] = df.loc[df["Date"].dt.strftime("%b") == month].shape[0]

        return data
