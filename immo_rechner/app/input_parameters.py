from dash import html, dcc


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
