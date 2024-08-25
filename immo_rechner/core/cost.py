from abc import ABC
from typing import Optional

from immo_rechner.core.abstract_position import AbstractPosition


class BuildingMaintenance(AbstractPosition):
    """
    BuildingMaintenance corresponds to Hausgeld.
    """

    def __init__(
            self, monthly_cost: Optional[int] = None, yearly_cost: Optional[int] = None
    ):
        if (not monthly_cost) and (not yearly_cost):
            raise ValueError("Either monthly_cost or yearly_cost should be not None.")

        self.yearly_cost = monthly_cost * 12

    def evaluate(self, *args, **kwargs):
        return self.yearly_cost


class InterestRate(AbstractPosition):
    N_MONTHS = 12

    def __init__(
            self, yearly_rate: float, repayment_amount: float, initial_debt: float
    ):
        self.yearly_rate = yearly_rate
        self.remaining_debt = initial_debt
        self.repayment_amount = repayment_amount
        self.initial_debt = initial_debt

    def reset(self):
        self.remaining_debt = self.initial_debt

    def pay_interest_per_month(self):
        cost = (self.yearly_rate / self.N_MONTHS) * self.remaining_debt
        self.remaining_debt -= self.repayment_amount - cost

        return cost

    def evaluate(self, *args, **kwargs):
        total_costs = 0
        for _ in range(self.N_MONTHS):
            total_costs += self.pay_interest_per_month()

        return total_costs


class PurchaseCost(AbstractPosition, ABC):

    def __init__(
            self,
            purchase_price: float,
            land_value: Optional[float] = None,
            approximate_land_value: bool = True,
    ):
        self.purchase_price = purchase_price
        if (land_value is None) and (not approximate_land_value):
            raise ValueError(f"land_value is None and approximate_land_value is False.")

        self.land_value = 0.2 * self.purchase_price if approximate_land_value else land_value


class AccusationCost(PurchaseCost):

    def __init__(
            self,
            purchase_price: float,
            land_value: Optional[float] = None,
            approximate_land_value: bool = True,
            makler: float = 0.0357,
            notar: float = 0.015,
            transfer_tax: float = 0.06,
    ):
        super().__init__(purchase_price=purchase_price, land_value=land_value,
                         approximate_land_value=approximate_land_value)
        self.makler = makler
        self.notar = notar
        self.transfer_tax = transfer_tax

    def evaluate(self, *args, **kwargs):
        return (self.makler + self.notar + self.transfer_tax) * self.purchase_price
