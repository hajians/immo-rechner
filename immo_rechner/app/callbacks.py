from typing import Iterable

import numpy as np
import plotly.graph_objects as go
from plotly import express
from plotly.subplots import make_subplots

from immo_rechner.core.profit_calculator import InputParameters, ProfitCalculator
from immo_rechner.core.tax_contexts import UsageContext
from immo_rechner.core.utils import get_logger

logger = get_logger(__name__)


def disable_repayment_range_or_value(repayment_value):
    if repayment_value:
        return True, False
    else:
        return False, True


def disable_monthly_rent(apt_own_usage):
    if UsageContext(apt_own_usage) == UsageContext.OWN_USE:
        return True, 0
    elif UsageContext(apt_own_usage) == UsageContext.RENTING:
        return False, 1500
    else:
        raise ValueError(f"Usage not defined: {apt_own_usage}")


def use_own_capital(use_own_capital):
    if use_own_capital:
        return True, False
    else:
        return False, True


def get_color_map(names: Iterable):
    return {n: c for n, c in zip(names, express.colors.qualitative.Alphabet)}


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
    use_repayment_range,
    repayment_value,
    apt_own_usage,
    own_capital_box,
    own_capital,
):
    fig = make_subplots(rows=2, cols=2)

    usage = UsageContext(apt_own_usage)
    logger.info(f"Using Tax context {usage}")

    if use_repayment_range:
        repayments = np.arange(*repayment_range, 500)
    else:
        repayments = np.array([repayment_value])

    color_maps = get_color_map(repayments)

    for repayment in repayments:
        input_parameters = InputParameters(
            usage=usage,
            yearly_income=yearly_income,
            monthly_rent=month_rent,
            facility_monthly_cost=facility_costs,
            owner_share=facility_costs_owner_share / 100,
            repayment_amount=repayment,
            yearly_interest_rate=interest_rate_percentage / 100,
            initial_debt=initial_debt,
            depreciation_rate=depreciation_precentage / 100,
            purchase_price=purchase_price,
            own_capital=own_capital if own_capital_box else None,
        )

        profit_calculater = ProfitCalculator.from_input_params(input_parameters)
        df = profit_calculater.simulate(n_years=num_years, to_pandas=True)
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
        fig.add_trace(
            go.Scatter(
                x=df.year,
                y=df.remaining_debt,
                marker=dict(color=color_maps[repayment]),
                showlegend=False,
            ),
            row=1,
            col=2,
        )

        fig.add_trace(
            go.Scatter(
                x=df.year,
                y=df.yearly_interest_cost,
                marker=dict(color=color_maps[repayment]),
                showlegend=False,
            ),
            row=2,
            col=2,
        )

    fig.add_annotation(
        text=f"Initial debt: {profit_calculater.initial_debt}",
        row=1,
        col=2,
        showarrow=False,
        x=0,
        y=0,
    )

    fig.update_layout(
        xaxis2_title=dict(text="Year"),
        yaxis2_title=dict(text="Remaining debt (EUR)"),
        yaxis3_title=dict(text="Tax benefit (EUR)"),
        yaxis4_title=dict(text="Yearly interest cost (EUR)"),
    )

    return fig
