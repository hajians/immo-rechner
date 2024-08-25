from abc import ABC, abstractmethod


class AbstractPosition(ABC):

    @property
    @abstractmethod
    def is_cashflow(self) -> bool:
        pass

    @abstractmethod
    def evaluate(self, *args, **kwargs) -> float:
        pass
