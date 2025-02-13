import os.path

import click
import dash_auth
from dash import Dash, html, dcc, Output, Input
from dotenv import dotenv_values
from flask import jsonify
import dash_bootstrap_components as dbc

from immo_rechner.app.callbacks import (
    disable_repayment_range_or_value,
    disable_monthly_rent,
    use_own_capital,
    update_graph,
)
from immo_rechner.app.input_parameters import (
    get_income_table,
    get_cost_table,
    get_additional_params,
)
from immo_rechner.core.utils import get_logger

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_PATH = os.path.join(FILE_DIR, "assets")

CSS_PATHS = [os.path.join(ASSET_PATH, "css", filename) for filename in ["w3.css"]] + [
    dbc.themes.BOOTSTRAP
]

logger = get_logger("app")


def health_check():
    return jsonify({"status": "healthy"}), 200


def get_app():
    app = Dash(__name__, external_stylesheets=CSS_PATHS)
    app.title = "Immobilien Rechner"
    app.layout = [
        html.H1(
            children="Immobilien Rechner", className="w3-container w3-2xlarge w3-center"
        ),
        html.P(
            children=[
                "This a web-based tool to "
                "help users calculate property investment outcomes, "
                "including mortgage payments, tax benefits, and cash flow projections. "
                "The app is ideal for property buyers, investors, and real estate agents. ",
                html.I("This tool is experimental, so use with care. "),
                html.A(
                    "Read this to understand how depreciation works in Germany.",
                    href="https://hypofriend.de/en/depreciation-laws-real-estate-germany-2024.add",
                ),
            ],
            className="w3-container w3-left w3-half w3-large",
        ),
        html.Table(
            className="w3-container w3-table w3-center",
            children=[
                html.Td(get_income_table()),
                html.Td(get_cost_table()),
                html.Td(get_additional_params()),
            ],
        ),
        html.Div(
            className="w3-container w3-center",
            children=dcc.Graph(id="graph-cashflow"),
        ),
    ]

    app.callback(
        Output("repayment-value", "disabled"),
        Output("repayment-range", "disabled"),
        Input("use-repayment-range", "value"),
    )(disable_repayment_range_or_value)

    app.callback(
        Output("monthly-rent", "disabled"),
        Output("monthly-rent", "value"),
        Input("apt-own-usage", "value"),
    )(disable_monthly_rent)

    app.callback(
        Output("initial-debt", "disabled"),
        Output("own-capital", "disabled"),
        Input("own-capital-box", "value"),
    )(use_own_capital)

    app.callback(
        Output("graph-cashflow", "figure"),
        Input("repayment-range", "value"),
        Input("yearly-income", "value"),
        Input("monthly-rent", "value"),
        Input("initial-debt", "value"),
        Input("num-years", "value"),
        Input("interest-rate", "value"),
        Input("facility-costs", "value"),
        Input("facility-costs-owner-share", "value"),
        Input("purchase-price", "value"),
        Input("depreciation-rate", "value"),
        Input("use-repayment-range", "value"),
        Input("repayment-value", "value"),
        Input("apt-own-usage", "value"),
        Input("own-capital-box", "value"),
        Input("own-capital", "value"),
        Input("makler-provision", "value"),
    )(update_graph)

    app.server.add_url_rule("/health", "health_check", health_check, methods=["GET"])

    secrets = dotenv_values()

    if secrets:
        dash_auth.BasicAuth(app, secrets)
    else:
        logger.info("No authentication was provided.")

    return app


def get_server():
    """
    Returns flask app for gunicorn.
    """

    app = get_app()
    return app.server


@click.command()
@click.option("--debug-mode", default=False, is_flag=True)
@click.option("--host", default="127.0.0.1", type=str)
@click.option("--port", default="8050", type=str)
def main(debug_mode, host, port):
    app = get_app()
    app.run(debug=debug_mode, host=host, port=port)


if __name__ == "__main__":
    main()
