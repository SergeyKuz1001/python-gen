import libcst
from dataclasses import dataclass
from typing import Optional, Callable


class AllowableFailure(Exception):
    def __init__(self, depth_of_raising: int = 0):
        self.depth_of_raising: int = depth_of_raising

    @property
    def in_this_node(self) -> bool:
        return self.depth_of_raising <= 0

    def emerge(self) -> None:
        self.depth_of_raising -= 1


class UnexpectedFailure(Exception):
    def __init__(self, real_failure: Exception):
        super().__init__(repr(real_failure))
