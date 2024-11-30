from abc import ABC
from typing import Optional

from immo_rechner.core.abstract_position import AbstractPosition
from immo_rechner.core.tax_contexts import RentingVsOwnUsageTaxContext, UsageContext

N_MONTHS = 12


class BuildingMaintenance(RentingVsOwnUsageTaxContext, AbstractPosition):
    """
    BuildingMaintenance corresponds to Hausgeld.
    """

    is_cashflow = True

    def __init__(
        self,
        usage: UsageContext,
        owner_share: float = 0.5,
        monthly_cost: Optional[float] = None,
        yearly_cost: Optional[float] = None,
    ):
        RentingVsOwnUsageTaxContext.__init__(self, usage=usage)

        if (not monthly_cost) and (not yearly_cost):
            raise ValueError("Either monthly_cost or yearly_cost should be not None.")

        self.yearly_cost = monthly_cost * N_MONTHS if monthly_cost else yearly_cost
        self.owner_share = owner_share

    def evaluate(self, *args, **kwargs):
        return self.apply_tax_context(-self.yearly_cost * self.owner_share)


class InterestRate(RentingVsOwnUsageTaxContext, AbstractPosition):
    """
    Class for computing interest rate
    """

    is_cashflow = True

    def __init__(
        self,
        usage: UsageContext,
        yearly_rate: float,
        repayment_amount: float,
        initial_debt: float,
    ):
        RentingVsOwnUsageTaxContext.__init__(self, usage=usage)

        self.yearly_rate = yearly_rate
        self.remaining_debt = initial_debt
        self.repayment_amount = repayment_amount
        self.initial_debt = initial_debt
        self.counter = 0

    def reset(self):
        self.remaining_debt = self.initial_debt

    def pay_interest_per_month(self):
        cost = (self.yearly_rate / N_MONTHS) * self.remaining_debt
        self.remaining_debt -= self.repayment_amount - cost

        self.counter += 1

        return cost

    def evaluate(self, *args, **kwargs):
        total_costs = 0
        for _ in range(N_MONTHS):
            total_costs += self.pay_interest_per_month()

        return self.apply_tax_context(-total_costs)


class PurchaseCost(RentingVsOwnUsageTaxContext, AbstractPosition):
    is_cashflow = False

    def __init__(
        self,
        usage: UsageContext,
        purchase_price: float,
        depreciation_rate: float,
        land_value: Optional[float] = None,
        approximate_land_value: bool = True,
    ):
        RentingVsOwnUsageTaxContext.__init__(self, usage=usage)

        self.purchase_price = purchase_price
        if (land_value is None) and (not approximate_land_value):
            raise ValueError(f"land_value is None and approximate_land_value is False.")

        self.land_value = (
            0.2 * self.purchase_price if approximate_land_value else land_value
        )

        self.depreciation_rate = depreciation_rate

    def evaluate(self, *args, **kwargs):
        return self.apply_tax_context(
            -self.depreciation_rate * (self.purchase_price - self.land_value)
        )


class PurchaseSideCost(PurchaseCost):

    def __init__(
        self,
        usage: UsageContext,
        purchase_price: float,
        depreciation_rate: float,
        land_value: Optional[float] = None,
        approximate_land_value: bool = True,
        makler: float = 0.0357,
        notar: float = 0.015,
        transfer_tax: float = 0.06,
    ):
        super().__init__(
            usage=usage,
            purchase_price=purchase_price,
            land_value=land_value,
            approximate_land_value=approximate_land_value,
            depreciation_rate=depreciation_rate,
        )
        self.makler = makler
        self.notar = notar
        self.transfer_tax = transfer_tax

    def evaluate(self, *args, **kwargs):
        return self.apply_tax_context(
            -(
                (self.makler + self.notar + self.transfer_tax)
                * (self.purchase_price - self.land_value)
                * self.depreciation_rate
            )
        )
