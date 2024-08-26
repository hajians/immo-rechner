from typing import List, Optional

from immo_rechner.core.abstract_position import AbstractPosition
from immo_rechner.core.cost import (
    BuildingMaintenance,
    InterestRate,
    PurchaseCost,
    PurchaseSideCost,
)
from immo_rechner.core.revenue import RentIncome
from immo_rechner.core.utils import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


class YearlySummary(BaseModel):
    cashflow: float
    profit_before_taxes: float
    income_tax: float


class ProfitCalculator:

    def __init__(self, positions: List[AbstractPosition], yearly_income: float):
        self.positions = positions
        self.yearly_income = yearly_income

    @staticmethod
    def get_yearly_income_tax(taxable_income: float):
        # TODO: Write a proper logic for this
        return 0.2 * taxable_income

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

        logger.info(f"Removing tax ({income_tax_diff}) from cashflow")
        cashflow -= income_tax_diff

        return YearlySummary(
            cashflow=cashflow,
            profit_before_taxes=profit_before_taxes,  # This includes depreciation.
            income_tax=income_tax_diff,
        )

    @classmethod
    def from_raw_data(
        cls,
        yearly_income: float,
        monthly_rent: float,
        facility_monthly_cost: float,
        owner_share: float,
        yearly_interest_rate: float,
        repayment_amount: float,
        initial_debt: float,
        purchase_price: float,
        land_value: Optional[float] = None,
        approximate_land_value: bool = True,
        depreciation_rate: float = 0.02,
        makler: float = 0.0357,
        notar: float = 0.015,
        transfer_tax: float = 0.06,
    ):
        positions = [
            RentIncome(monthly_rent=monthly_rent),
            BuildingMaintenance(
                owner_share=owner_share, monthly_cost=facility_monthly_cost
            ),
            InterestRate(
                yearly_rate=yearly_interest_rate,
                repayment_amount=repayment_amount,
                initial_debt=initial_debt,
            ),
            PurchaseCost(
                purchase_price=purchase_price,
                land_value=land_value,
                approximate_land_value=approximate_land_value,
                depreciation_rate=depreciation_rate,
            ),
            PurchaseSideCost(
                purchase_price=purchase_price,
                land_value=land_value,
                approximate_land_value=approximate_land_value,
                makler=makler,
                notar=notar,
                transfer_tax=transfer_tax,
                depreciation_rate=depreciation_rate,
            ),
        ]

        return cls(positions=positions, yearly_income=yearly_income)
