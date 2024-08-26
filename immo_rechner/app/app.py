import numpy as np
from dash import Dash, html, dcc, callback, Output, Input
from plotly.subplots import make_subplots

from immo_rechner.core.profit_calculator import ProfitCalculator
import plotly.graph_objects as go


def get_result(repayment_amount):
    return ProfitCalculator.from_raw_data(
        yearly_income=100_000,
        monthly_rent=1500,
        facility_monthly_cost=350.0,
        owner_share=0.5,
        repayment_amount=repayment_amount,
        yearly_interest_rate=0.035,
        initial_debt=450_000,
        depreciation_rate=0.02,
        purchase_price=500_000,
    )


def get_app():
    app = Dash()
    app.layout = [
        html.H1(children="Immobilien Rechner", style={"textAlign": "center"}),
        html.H2(
            children=[
                "Repayment (lower)",
                dcc.Textarea(id="repayment-value-lb", value="500.0"),
            ]
        ),
        html.H2(
            children=[
                "Repayment (upper)",
                dcc.Textarea(id="repayment-value-up", value="2000.0"),
            ]
        ),
        html.H2(
            children=[
                "Repayment (step)",
                dcc.Textarea(id="repayment-value-step", value="500.0"),
            ]
        ),
        dcc.Graph(id="graph-cashflow"),
    ]

    @callback(
        Output("graph-cashflow", "figure"),
        Input("repayment-value-lb", "value"),
        Input("repayment-value-up", "value"),
        Input("repayment-value-step", "value"),
    )
    def update_graph(repayment_lb, repayment_ub, repayment_step):
        repayment_lb = float(repayment_lb)
        repayment_ub = float(repayment_ub)
        step = float(repayment_step) if float(repayment_step) > 0 else 100

        fig = make_subplots(rows=2, cols=1)

        for repayment in np.arange(repayment_lb, repayment_ub, step):
            df = get_result(repayment).simulate(n_years=10, to_pandas=True)
            fig.add_trace(
                go.Scatter(x=df.year, y=df.cashflow, name=f"repayment: {repayment}"), row=1, col=1
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
