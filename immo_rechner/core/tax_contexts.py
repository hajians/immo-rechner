from abc import ABC, abstractmethod
from enum import Enum


class UsageContext(Enum):
    OWN_USE = "own_use"
    RENTING = "renting"


class TaxContext(ABC):

    usage: UsageContext

    @property
    @abstractmethod
    def is_tax_deductible(self) -> bool:
        pass


class RentingVsOwnUsageTaxContext(TaxContext):

    def __init__(self, usage: UsageContext):
        self.usage = usage

    def is_tax_deductible(self) -> bool:
        if self.usage not in [UsageContext.OWN_USE, UsageContext.RENTING]:
            raise ValueError(f"usage is not defined: {self.usage}")

        return True if self.usage == UsageContext.RENTING else False

class AlwaysAccountedTaxContext(TaxContext):

    usage = None

    def is_tax_deductible(self) -> bool:
        return True