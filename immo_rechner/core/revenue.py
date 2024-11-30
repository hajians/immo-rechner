from immo_rechner.core.abstract_position import AbstractPosition
from immo_rechner.core.tax_contexts import AlwaysAccountedTaxContext

N_MONTHS = 12


class RentIncome(AlwaysAccountedTaxContext, AbstractPosition):
    is_cashflow = True

    def __init__(self, monthly_rent: float):
        self.yearly_rent = monthly_rent * N_MONTHS

    def evaluate(self, *args, **kwargs) -> float:
        return self.yearly_rent
