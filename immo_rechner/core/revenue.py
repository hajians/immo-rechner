from immo_rechner.core.abstract_position import AbstractPosition

N_MONTHS = 12


class RentIncome(AbstractPosition):
    is_cashflow = True

    def __init__(self, monthly_rent: float):
        self.yearly_rent = monthly_rent * N_MONTHS

    def evaluate(self, *args, **kwargs) -> float:
        return self.yearly_rent
