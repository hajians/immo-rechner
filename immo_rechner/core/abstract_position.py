from abc import ABC, abstractmethod


class AbstractPosition(ABC):
    @abstractmethod
    def evaluate(self, *args, **kwargs):
        pass
