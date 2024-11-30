from abc import ABC, abstractmethod
from enum import Enum


class UsageContext(Enum):
    OWN_USE = "own_use"
    RENTING = "renting"


class TaxContext(ABC):

    @property
    @abstractmethod
    def is_tax_deductible(self) -> bool:
        pass

    def apply_tax_context(self, value: float) -> float:
        return value if self.is_tax_deductible else 0.0


class RentingVsOwnUsageTaxContext(TaxContext):

    def __init__(self, usage: UsageContext):
        self.usage = usage

    @property
    def is_tax_deductible(self) -> bool:
        if self.usage not in [UsageContext.OWN_USE, UsageContext.RENTING]:
            raise ValueError(f"usage is not defined: {self.usage}")

        return True if self.usage == UsageContext.RENTING else False
