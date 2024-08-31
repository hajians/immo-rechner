import os.path
from typing import Iterable

import numpy as np
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input
from plotly import express
from plotly.subplots import make_subplots

from immo_rechner.app.input_parameters import (
    get_income_table,
    get_cost_table,
    get_additional_params,
)
from immo_rechner.core.profit_calculator import ProfitCalculator, InputParameters

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_PATH = os.path.join(FILE_DIR, "assets")

CSS_PATHS = [os.path.join(ASSET_PATH, "css", filename) for filename in ["w3.css"]]


def get_color_map(names: Iterable):
    return {n: c for n, c in zip(names, express.colors.qualitative.Alphabet)}


def get_app():
    app = Dash(__name__, external_stylesheets=CSS_PATHS)
    app.title = "Immobilien Rechner"
    app.layout = [
        html.H1(
            children="Immobilien Rechner", className="w3-container w3-2xlarge w3-center"
        ),
        html.Div(
            className="w3-row w3-center",
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

    @callback(
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
    )
    def update_graph(
        repayment_range,
        yearly_income,
        month_rent,
        initial_debt,
        num_years,
        interest_rate_percentage,
        facility_costs,
        facility_costs_owner_share,
        purchase_price,
        depreciation_precentage,
    ):
        fig = make_subplots(rows=2, cols=1)

        repayments = np.arange(*repayment_range, 500)
        color_maps = get_color_map(repayments)

        for repayment in repayments:
            input_parameters = InputParameters(
                yearly_income=yearly_income,
                monthly_rent=month_rent,
                facility_monthly_cost=facility_costs,
                owner_share=facility_costs_owner_share / 100,
                repayment_amount=repayment,
                yearly_interest_rate=interest_rate_percentage / 100,
                initial_debt=initial_debt,
                depreciation_rate=depreciation_precentage / 100,
                purchase_price=purchase_price,
            )
            df = ProfitCalculator.from_raw_data(**input_parameters.dict()).simulate(
                n_years=num_years, to_pandas=True
            )
            fig.add_trace(
                go.Scatter(
                    x=df.year,
                    y=df.cashflow,
                    name=f"repayment: {repayment}",
                    marker=dict(color=color_maps[repayment]),
                ),
                row=1,
                col=1,
            ).update_layout(
                yaxis_title=dict(text="Cash flow (EUR)"),
            )
            fig.add_trace(
                go.Scatter(
                    x=df.year,
                    y=df.tax_benefit,
                    marker=dict(color=color_maps[repayment]),
                    showlegend=False,
                ),
                row=2,
                col=1,
            )

        fig.update_layout(
            xaxis2_title=dict(text="Year"),
            yaxis2_title=dict(text="Tax benefit (EUR)"),
        )

        return fig

    return app


if __name__ == "__main__":
    app = get_app()
    app.run(debug=True)
