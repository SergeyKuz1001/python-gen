from .abstract import AbstractChecker

from abc import ABC, abstractmethod


class RuleChecker(AbstractChecker, ABC):
    @abstractmethod
    def in_rules(self, rules: list[str]) -> bool: ...
