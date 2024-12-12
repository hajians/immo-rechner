from dash import html, dcc

from immo_rechner.core.tax_contexts import UsageContext


def get_income_table():
    return html.Table(
        className="w3-table w3-bordered",
        children=[
            html.Th("Revenues", colSpan=2, className="w3-teal"),
            html.Tr(
                children=[
                    html.Td("Yearly income"),
                    html.Td(
                        dcc.Input(
                            id="yearly-income",
                            value=100000,
                            type="number",
                            min=1,
                            step=1,
                        ),
                    ),
                ]
            ),
            html.Tr(
                children=[
                    html.Td("Monthly rent "),
                    html.Td(
                        dcc.Input(
                            id="monthly-rent", value=1500, type="number", min=0, step=1
                        )
                    ),
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
                    html.Td("Purchase price"),
                    html.Td(
                        dcc.Input(
                            500000, min=0, step=1, id="purchase-price", type="number"
                        )
                    ),
                ]
            ),
            html.Tr(
                children=[
                    html.Td("Own capital (Eigenkapital)"),
                    html.Td(
                        dcc.Input(
                            id="own-capital",
                            value=100000,
                            min=1,
                            type="number",
                            step=1,
                        )
                    ),
                    dcc.Checklist(
                        options=["Use own capital"], value=[], id="own-capital-box"
                    ),
                ]
            ),
            html.Tr(
                children=[
                    html.Td("Initial loan amount"),
                    html.Td(
                        dcc.Input(
                            id="initial-debt",
                            value=450000,
                            min=1,
                            type="number",
                            step=1,
                        )
                    ),
                    html.Td("Yearly interest rate (%)"),
                    html.Td(
                        dcc.Input(
                            3.55,
                            min=0,
                            max=100,
                            step=0.01,
                            id="interest-rate",
                            type="number",
                        )
                    ),
                ],
            ),
            html.Tr(
                children=[
                    html.Td("Loan repayment range"),
                    html.Td(
                        html.Div(
                            className="w3-container w3-col",
                            children=[
                                html.Div(
                                    className="w3-container w3-row-padding",
                                    children=[
                                        dcc.Input(
                                            1500,
                                            min=0,
                                            step=1,
                                            id="repayment-value",
                                            type="number",
                                            className="w3-half",
                                        ),
                                        dcc.Checklist(
                                            options=["Use Range"],
                                            value=[],
                                            id="use-repayment-range",
                                            className="w3-half",
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="w3-container w3-row w3-padding-16",
                                    children=[
                                        dcc.RangeSlider(
                                            min=500,
                                            max=3000,
                                            step=500,
                                            value=[500, 1500],
                                            id="repayment-range",
                                        )
                                    ],
                                ),
                            ],
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
                    html.Td("Owner's share (%)"),
                    html.Td(
                        dcc.Input(
                            50,
                            min=0,
                            max=100,
                            step=1,
                            id="facility-costs-owner-share",
                            type="number",
                        )
                    ),
                ]
            ),
            html.Tr(
                children=[
                    html.Td("Depreciation rate (%) per year (for taxes)"),
                    html.Td(
                        dcc.Input(
                            2,
                            min=0,
                            max=100,
                            step=1,
                            id="depreciation-rate",
                            type="number",
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
            html.Tr(
                children=[
                    html.Td(
                        dcc.Dropdown(
                            options=[
                                UsageContext.OWN_USE.value,
                                UsageContext.RENTING.value,
                            ],
                            value=UsageContext.RENTING.value,
                            clearable=False,
                            id="apt-own-usage",
                        ),
                    )
                ]
            ),
        ],
    )
