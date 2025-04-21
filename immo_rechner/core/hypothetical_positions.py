from immo_rechner.core.abstract_position import AbstractPosition
from immo_rechner.core.tax_contexts import RentingVsOwnUsageTaxContext, UsageContext

N_MONTHS = 12


class HypotheticalRentIncome(AbstractPosition, RentingVsOwnUsageTaxContext):
    is_cashflow = False

    def __init__(self, monthly_rent: float, usage: UsageContext):
        RentingVsOwnUsageTaxContext.__init__(self, usage=usage)
        self.yearly_rent = monthly_rent * N_MONTHS

    def evaluate(self, *args, **kwargs) -> float:
        return self.yearly_rent


class HypotheticalAppreciation(AbstractPosition, RentingVsOwnUsageTaxContext):
    is_cashflow = False

    def __init__(
        self, appreciation_rate: float, initial_price: float, usage: UsageContext
    ):
        RentingVsOwnUsageTaxContext.__init__(self, usage=usage)
        self.initial_price = initial_price
        self.appreciation_rate = appreciation_rate

        self.current_price = self.initial_price

    def reset(self):
        self.current_price = self.initial_price

    def evaluate(self, *args, **kwargs) -> float:
        appreciation = self.current_price * self.appreciation_rate
        self.current_price += appreciation
        return appreciation
