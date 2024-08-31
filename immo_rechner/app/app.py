import os.path

import numpy as np
from dash import Dash, html, dcc, callback, Output, Input
from plotly.subplots import make_subplots

from immo_rechner.core.profit_calculator import ProfitCalculator, InputParameters
import plotly.graph_objects as go

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_PATH = os.path.join(FILE_DIR, "assets")

CSS_PATHS = [os.path.join(ASSET_PATH, "css", filename) for filename in ["w3.css"]]


def get_income_table():
    return html.Table(
        className="w3-table w3-bordered",
        children=[
            html.Th("Revenues", colSpan=2, className="w3-teal"),
            html.Tr(
                children=[
                    html.Td("Yearly income"),
                    html.Td(
                        dcc.Textarea(id="yearly-income", value="100000"),
                    ),
                ]
            ),
            html.Tr(
                children=[
                    html.Td("Monthly rent "),
                    html.Td(dcc.Textarea(id="monthly-rent", value="1500.0")),
                ]
            ),
        ],
    )


def get_cost_table():
    return html.Table(
        className="w3-table w3-bordered",
        children=[
            html.Th("Costs", colSpan=4, className="w3-red"),
            html.Tr(
                children=[
                    html.Td("Initial loan amount"),
                    html.Td(dcc.Textarea(id="initial-debt", value="450000")),
                    html.Td("Yearly interest rate"),
                    html.Td(
                        dcc.Textarea(id="interest-rate", value="0.035"),
                    ),
                ],
            ),
            html.Tr(
                children=[
                    html.Td("Loan repayment range"),
                    html.Td(
                        dcc.RangeSlider(
                            min=500,
                            max=3000,
                            step=500,
                            value=[500, 1500],
                            id="repayment-range",
                        ),
                        colSpan=3,
                    ),
                ]
            ),
            html.Tr(
                children=[
                    html.Td("Facility monthly costs (Hausgeld)"),
                    html.Td(
                        dcc.Input(
                            350, min=0, step=1, id="facility-costs", type="number"
                        )
                    ),
                ]
            ),
            html.Tr(
                children=[
                    html.Td("Purchase price"),
                    html.Td(
                        dcc.Input(
                            500000, min=0, step=1, id="purchase-price", type="number"
                        )
                    ),
                ]
            ),
        ],
    )


def get_additional_params():
    return html.Table(
        className="w3-table w3-bordered",
        children=[
            html.Th("Simulation parameters", colSpan=2, className="w3-blue"),
            html.Tr(
                children=[
                    html.Td("Number of years"),
                    html.Td(
                        dcc.Input(
                            10, min=5, max=100, step=1, id="num-years", type="number"
                        )
                    ),
                ],
            ),
        ],
    )


def get_app():
    app = Dash(__name__, external_stylesheets=CSS_PATHS)
    app.title = "Immobilien Rechner"
    app.layout = [
        html.H1(
            children="Immobilien Rechner", className="w3-container w3-2xlarge w3-center"
        ),
        html.Table(
            className="w3-container w3-table w3-center",
            children=[
                html.Td(get_income_table()),
                html.Td(get_cost_table()),
                html.Td(get_additional_params()),
            ],
        ),
        dcc.Graph(id="graph-cashflow"),
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
        Input("purchase-price", "value"),
    )
    def update_graph(
        repayment_range,
        yearly_income,
        month_rent,
        initial_debt,
        num_years,
        interest_rate,
        facility_costs,
        purchase_price,
    ):
        fig = make_subplots(rows=2, cols=1)

        for repayment in np.arange(*repayment_range, 500):
            input_parameters = InputParameters(
                yearly_income=yearly_income,
                monthly_rent=month_rent,
                facility_monthly_cost=facility_costs,
                owner_share=0.5,
                repayment_amount=repayment,
                yearly_interest_rate=interest_rate,
                initial_debt=initial_debt,
                depreciation_rate=0.02,
                purchase_price=purchase_price,
            )
            df = ProfitCalculator.from_raw_data(**input_parameters.dict()).simulate(
                n_years=num_years, to_pandas=True
            )
            fig.add_trace(
                go.Scatter(x=df.year, y=df.cashflow, name=f"repayment: {repayment}"),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df.year, y=df.tax_benefit, name=f"tax benefit: {repayment}"
                ),
                row=2,
                col=1,
            )

        return fig

    return app


if __name__ == "__main__":
    app = get_app()
    app.run(debug=True)
