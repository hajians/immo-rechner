from typing import List, Optional, Union

import pandas as pd
from pydantic import BaseModel, computed_field

from immo_rechner.core.abstract_position import AbstractPosition
from immo_rechner.core.cost import (
    BuildingMaintenance,
    InterestRate,
    PurchaseCost,
    PurchaseSideCost,
)
from immo_rechner.core.revenue import RentIncome
from immo_rechner.core.tax_contexts import UsageContext
from immo_rechner.core.utils import get_logger

logger = get_logger(__name__)


class YearlySummary(BaseModel):
    cashflow: float
    profit_before_taxes: float
    income_tax: float
    remaining_debt: Optional[float] = None
    cumulative_interest_cost: Optional[float] = None
    yearly_interest_cost: Optional[float] = None

    @computed_field
    @property
    def tax_benefit(self) -> float:
        return -self.income_tax


class InputParameters(BaseModel):
    usage: UsageContext
    yearly_income: float
    monthly_rent: float
    facility_monthly_cost: float
    owner_share: float
    yearly_interest_rate: float
    repayment_amount: float
    initial_debt: float
    purchase_price: float
    own_capital: Optional[float] = None
    land_value: Optional[float] = None
    approximate_land_value: bool = True
    depreciation_rate: float = 0.02
    makler: float = 0.0357
    notar: float = 0.015
    transfer_tax: float = 0.06


class ProfitCalculator:

    @staticmethod
    def fetch_interest_rate_position(positions: List[AbstractPosition]) -> InterestRate:
        for item in positions:
            if isinstance(item, InterestRate):
                logger.info(
                    f"InterestRate object found: {item}; ignoring next positions."
                )
                return item

    def __init__(self, positions: List[AbstractPosition], yearly_income: float):
        self.positions = positions
        self.yearly_income = yearly_income

        self.interest_rate_position = self.fetch_interest_rate_position(self.positions)
        self.initial_debt = self.interest_rate_position.initial_debt

    @staticmethod
    def get_yearly_income_tax(taxable_income: float) -> float:
        """
        Formula is taken from here:
            https://www.finanz-tools.de/einkommensteuer/berechnung-formeln/2024
        :param taxable_income:
        :return:
        """
        if 277_826 <= taxable_income:
            return 0.45 * taxable_income - 18_936.88
        elif 66_761 <= taxable_income < 277_826:
            return 0.42 * taxable_income - 10_602.13
        elif 17_006 <= taxable_income < 66_761:
            z = (taxable_income - 17_005) / 10_000
            return (181.19 * z + 2397) * z + 1025.38
        elif 11_605 <= taxable_income < 17_006:
            z = (taxable_income - 11_605) / 10_000
            return (922.98 * z + 1400) * z
        elif taxable_income < 11_605:
            return 0.0
        else:
            raise ValueError(f"taxable_income {taxable_income} is not acceptable.")

    def yearly_simulation(self):
        profit_before_taxes = 0
        cashflow = 0
        for position in self.positions:
            value = position.evaluate()
            profit_before_taxes += value
            cashflow += value if position.is_cashflow else 0.0

        income_tax_diff = self.get_yearly_income_tax(
            self.yearly_income + profit_before_taxes
        ) - self.get_yearly_income_tax(self.yearly_income)

        logger.debug(f"Removing tax ({income_tax_diff}) from cashflow")
        cashflow -= income_tax_diff

        return YearlySummary(
            cashflow=cashflow,
            profit_before_taxes=profit_before_taxes,  # This includes depreciation.
            income_tax=income_tax_diff,
            remaining_debt=self.interest_rate_position.remaining_debt,
            cumulative_interest_cost=self.interest_rate_position.total_interest_cost,
            yearly_interest_cost=self.interest_rate_position.this_year_interest_cost,
        )

    def simulate(
        self, n_years: int, to_pandas: bool = False
    ) -> Union[List, pd.DataFrame]:
        output = []
        for year in range(1, n_years + 1):
            output.append(dict(year=year, **self.yearly_simulation().model_dump()))

        if to_pandas:
            return pd.DataFrame.from_records(output)

        return output

    @classmethod
    def from_input_params(cls, input_params: InputParameters):

        params = input_params.model_copy()

        if params.own_capital is not None:
            logger.info(f"Ignoring initial_debt: {params.initial_debt}")
            params.initial_debt = (
                params.purchase_price
                - params.own_capital
                + PurchaseSideCost.compute_side_costs(
                    makler=params.makler,
                    notar=params.notar,
                    transfer_tax=params.transfer_tax,
                    purchase_price=params.purchase_price,
                )
            )

        positions = [
            RentIncome(monthly_rent=params.monthly_rent),
            BuildingMaintenance(
                usage=params.usage,
                owner_share=params.owner_share,
                monthly_cost=params.facility_monthly_cost,
            ),
            InterestRate(
                usage=params.usage,
                yearly_rate=params.yearly_interest_rate,
                repayment_amount=params.repayment_amount,
                initial_debt=params.initial_debt,
            ),
            PurchaseCost(
                usage=params.usage,
                purchase_price=params.purchase_price,
                land_value=params.land_value,
                depreciation_rate=params.depreciation_rate,
            ),
            PurchaseSideCost(
                usage=params.usage,
                purchase_price=params.purchase_price,
                land_value=params.land_value,
                approximate_land_value=params.approximate_land_value,
                makler=params.makler,
                notar=params.notar,
                transfer_tax=params.transfer_tax,
                depreciation_rate=params.depreciation_rate,
            ),
        ]

        return cls(positions=positions, yearly_income=params.yearly_income)
