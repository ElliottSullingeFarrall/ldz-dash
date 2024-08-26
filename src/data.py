from __future__ import annotations

from calendar import month_abbr
from datetime import datetime
from html import unescape
from types import TracebackType
from typing import Optional

from flask_login import current_user  # type: ignore
from pandas import DataFrame, concat, read_csv, to_datetime
from pandas.errors import EmptyDataError

from .settings import DATA_DIR, TEMPLATES_DIR

DATA_TEMPLATES = TEMPLATES_DIR / "data"


class Data:
    categories = {
        dir.name: [path.stem for path in dir.iterdir()]
        for dir in (DATA_TEMPLATES).iterdir()
        if dir.is_dir()
    }

    def __init__(self, category: str, subcategory: str, username: Optional[str] = None) -> None:
        self.category = category
        self.subcategory = subcategory

        if username:
            self.username = username
        else:
            self.username = current_user.username

        self.path = (DATA_DIR / self.username / category / unescape(subcategory)).with_suffix(".csv")
        if self.path.exists():
            try:
                self._table = read_csv(self.path, index_col=False)
            except EmptyDataError:
                self._table = DataFrame()
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._table = DataFrame()

    def __enter__(self) -> Data:
        return self

    def __exit__(self, exception_type: Optional[type[BaseException]], exception_value: Optional[BaseException], exception_traceback: Optional[TracebackType]) -> None:
        self._table.to_csv(self.path, index=False)

    def append(self, row: dict) -> None:
        self._table = concat([DataFrame(row, index=[0]), self._table], ignore_index=True)
        self._table.sort_values("Date", ascending=False, inplace=True)

    def __delitem__(self, idx: int) -> None:
        self._table = self._table.drop(idx)
        self._table.sort_values("Date", ascending=False, inplace=True)

    @property
    def columns(self) -> list:
        return self._table.columns.tolist()

    @property
    def values(self) -> list:
        return self._table.values.tolist()

    @classmethod
    def pull(cls, form: dict) -> DataFrame:
        # For exporting user data
        dt = datetime.strptime(form["month"], "%Y-%m")
        category, type = form["category:type"].split(":")
        users = form.getlist("users") # type: ignore

        table = DataFrame()
        for user in users:
            with cls(category, type, user) as data:
                table = concat([table, data._table])

        if "Date" in table:
            table["Date"] = to_datetime(table["Date"])
            table = table.loc[(table["Date"].dt.month == dt.month) & (table["Date"].dt.year == dt.year)]
            table.sort_values("Date", ascending=False, inplace=True)

        return table

    def summarise(self, year: int) -> dict:
        # For using data in charts
        data = dict.fromkeys(month_abbr[1:], 0)

        if not self._table.empty:
            table = self._table.copy()

            table["Date"] = to_datetime(table["Date"])
            table = table[table["Date"].dt.year == year]

            for month in data:
                data[month] = table.loc[table["Date"].dt.strftime("%b") == month].shape[0]

        return data
