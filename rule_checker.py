from abstract_checker import AbstractChecker
from generator import Generator

from abc import ABC, abstractmethod


class RuleChecker(AbstractChecker, ABC):
    @abstractmethod
    def in_rules(self, rules: list[str], generator: Generator) -> bool: ...
