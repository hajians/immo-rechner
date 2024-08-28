import numpy as np
from dash import Dash, html, dcc, callback, Output, Input
from plotly.subplots import make_subplots

from immo_rechner.core.profit_calculator import ProfitCalculator, InputParameters
import plotly.graph_objects as go


def get_app():
    app = Dash()
    app.title = "Immobilien Rechner"
    app.layout = [
        html.H1(children="Immobilien Rechner", style={"textAlign": "center"}),
        html.H2(
            children=[
                "Yearly income ",
                dcc.Textarea(id="yearly-income", value="100000"),
            ]
        ),
        html.H2(
            children=[
                "(Repayment) upper ",
                dcc.Textarea(id="repayment-value-up", value="2000.0"),
                "lower ",
                dcc.Textarea(id="repayment-value-lb", value="500.0"),
                "step ",
                dcc.Textarea(id="repayment-value-step", value="500.0"),
            ]
        ),
        html.H2(
            children=[
                "Monthly rent ",
                dcc.Textarea(id="monthly-rent", value="1500.0"),
                "Initial debt ",
                dcc.Textarea(id="initial-debt", value="450000"),
            ]
        ),
        html.H2(
            children=[
                "Number of years",
                dcc.Slider(5, 30, 5, value=10, id="num-years"),
            ]
        ),
        dcc.Graph(id="graph-cashflow"),
    ]

    @callback(
        Output("graph-cashflow", "figure"),
        Input("repayment-value-lb", "value"),
        Input("repayment-value-up", "value"),
        Input("repayment-value-step", "value"),
        Input("yearly-income", "value"),
        Input("monthly-rent", "value"),
        Input("initial-debt", "value"),
        Input("num-years", "value"),
    )
    def update_graph(
        repayment_lb,
        repayment_ub,
        repayment_step,
        yearly_income,
        month_rent,
        initial_debt,
        num_years,
    ):
        repayment_lb = float(repayment_lb)
        repayment_ub = float(repayment_ub)
        step = float(repayment_step) if float(repayment_step) > 0 else 100

        fig = make_subplots(rows=2, cols=1)

        for repayment in np.arange(repayment_lb, repayment_ub, step):
            input_parameters = InputParameters(
                yearly_income=yearly_income,
                monthly_rent=month_rent,
                facility_monthly_cost=350.0,
                owner_share=0.5,
                repayment_amount=repayment,
                yearly_interest_rate=0.035,
                initial_debt=initial_debt,
                depreciation_rate=0.02,
                purchase_price=500_000,
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
