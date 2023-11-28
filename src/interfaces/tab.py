from abc import ABC, abstractmethod


class Tab(ABC):
    @abstractmethod
    def show(self) -> None:
        ...
