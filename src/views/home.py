from flask import Blueprint, jsonify, render_template

from src.data import Data

from . import View, login_required

home = Blueprint("home", __name__, template_folder="../templates/home")

@home.route("/")
@login_required
def index() -> View:
    return render_template("index.html")

@home.route("/charts/<category>/<type>/<int:year>", methods=["GET"])
@login_required
def charts(category: str, type: str, year: int) -> View:
    with Data(category, type) as data:
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
        "title": f"{category.capitalize()} - {type.upper()}",
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
