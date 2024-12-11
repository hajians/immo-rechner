from abc import ABC, abstractmethod
from enum import Enum


class UsageContext(Enum):
    OWN_USE = "Own usage"
    RENTING = "Renting"


class TaxContext(ABC):

    @abstractmethod
    def apply_tax_context(self, value: float) -> float:
        pass


class RentingVsOwnUsageTaxContext(TaxContext):

    def __init__(self, usage: UsageContext):
        self.usage = usage

    def apply_tax_context(self, value: float) -> float:
        if self.usage not in [UsageContext.OWN_USE, UsageContext.RENTING]:
            raise ValueError(f"usage is not defined: {self.usage}")

        return value if self.usage == UsageContext.RENTING else 0.0
