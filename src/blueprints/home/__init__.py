from os.path import join

from flask import Blueprint, jsonify, render_template

from src.data import Data
from src.view import View, login_required

TEMPLATES_DIR = "home"

home = Blueprint("home", __name__, url_prefix="/home")

@home.route("/")
@login_required
def index() -> View:
    return render_template(join(TEMPLATES_DIR, "index.html"))

@home.route("/charts/<category>/<subcategory>/<int:year>", methods=["GET"])
@login_required
def charts(category: str, subcategory: str, year: int) -> View:
    with Data(category, subcategory) as data:
        chart_data = data.summarise(year)

    trace = {
        "x": list(chart_data.keys()),
        "y": list(chart_data.values()),
        "type": "scatter",
        "mode": "lines+markers",
    }
    layout = {
        "paper_bgcolor": "transparent",
        "plot_bgcolor": "transparent",
        "showlegend": False,
        "autosize": True,
        "margin": {"l": 10, "r": 10, "t": 40, "b": 40},
        "title": f"{category.capitalize()} - {subcategory.upper()}",
        "xaxis": {
            "tickmode": "linear",
            "tick0": 0,
            "dtick": 1,
        },
        "yaxis": {
            "title": "# Students",
            "range": [0, "auto"],
            "rangemode": "tozero",
            "tickmode": "linear",
            "tick0": 0,
            "dtick": 1,
        },
    }

    return jsonify({"data": [trace], "layout": layout})
