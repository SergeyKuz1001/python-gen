from abc import ABC, abstractmethod


class AbstractAdapter(ABC):
    @property
    @abstractmethod
    def identifier(self) -> str: ...

    @abstractmethod
    def get_rules(self, filename: str) -> list[str]: ...
