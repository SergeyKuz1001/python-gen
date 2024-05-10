from .abstract import AbstractChecker

from abc import ABC


class StateViaMidRecChecker(AbstractChecker, ABC):
    def __init__(self):
        self._states: list[any] = []

    @property
    def state(self) -> any:
        return self._states.pop()

    @state.setter
    def state(self, value: any) -> None:
        return self._states.append(value)
